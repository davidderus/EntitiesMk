#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import subprocess
import re
import sys, os, glob, shutil

######################################################
# Colorize 1.0
# Generates syntax to display colors in Terminal
######################################################

# Main function, accepting a text, a color in text, and boolean options like bold or highlight 
def colorize(text, color, bold = False, highlight = False):
	# First Color, then Text
	colorModel = '\033[%sm%s\033[1;m'
	# Accepted color in a terminal
	colorList = {
		'gray': '30',
		'red': '31',
		'green': '32',
		'yellow': '33',
		'blue': '34',
		'magenta': '35',
		'cyan': '36',
		'white': '37',
		'crimson': '38'
	}
	# Checking if we output text in a TTY
	if not sys.stdout.isatty(): return text
	# Putting the dict value in a var
	foundColor = colorList[color]
	# Making the colorvalue string for the output 
	colorValue = ';'.join([str(int(bold)), foundColor if not highlight else str(int(foundColor)+10)])
	# Returning the formated string
	return colorModel % (colorValue, text)

######################################################
# EntitiesMk 1.0
# Auto-generates a bundle and all its components (Entities, Forms, Templates…) in one command-line.
######################################################

# Arguments parser
parser = argparse.ArgumentParser(description = 'Hand-made Symfony 2 all-in-one generator.')
parser.add_argument('--bundle-name', help = 'Bundle name', required = True)
parser.add_argument('--symfony', help = 'Path to Symfony project if not current directory', default = os.getcwd())
parser.add_argument('--format', help = 'The format use for your entities (yml, xml or annotation)', default = 'annotation')
parser.add_argument('--no-ts', help = 'Prevent auto-insert of the toString method to the entities', default = False, action = 'store_true')
parser.add_argument('--rollback', help = 'Undo change made to the directory (WARNING: Needs git. Will erase uncommited changes).', default = False, action = 'store_true')
args = parser.parse_args()

basePath = args.symfony
consolePath = os.path.normpath(basePath + os.sep + 'app/console')
# Checkin if basePath is okay
if not os.path.isfile(consolePath):
	print colorize('Your symfony path appears to be inexistant, check it again', 'red')
	sys.exit(0)

# Setting required varz
bundleName = args.bundle_name
entitiesFormat = args.format

# Creating namespace name
namespaceRoot = re.findall('[A-Z][^A-Z]*', bundleName)
namespace = '%s/%s' % (namespaceRoot[0], ''.join(namespaceRoot[1:]))

# If rollback
if args.rollback:
	bundleDir = basePath + os.sep + 'src' + os.sep + namespace
	if not os.path.exists(bundleDir):
		print colorize('Bundle not found, no rollback.', 'red')
		sys.exit(0)
	print colorize('Doing rollback. All uncommited changes will be lost.', 'red')
	# Removing files modifications
	print colorize('Checkouting repository', 'blue')
	os.chdir(basePath)
	subprocess.call(['git', 'checkout',  '.'])
	# Removing created directory based on the bundle name
	print colorize('Removing bundle', 'blue')
	shutil.rmtree(bundleDir)
	print colorize('Done, exiting!', 'blue')
	sys.exit(0)

# Printing some infos to the user
print colorize('Making %s' % bundleName, 'green', bold = True)
print colorize('Namespace: %s\r\n' % namespace, 'green')

# Setting up cmds
coreCmds = [
	{'cmd': [consolePath, 'generate:bundle', '--namespace=' + namespace, '--dir=' + basePath + os.sep + 'src', '--format=' + entitiesFormat, '--structure', '--no-interaction'], 'descr': 'Creating Bundle'},
	{'cmd': [consolePath,  'doctrine:mapping:convert', 'xml', os.path.normpath(basePath + '/src/' + namespace + '/Resources/config/doctrine/metadata/orm'), '--from-database', '--force'], 'descr': 'Getting database informations from xml'},
	{'cmd': [consolePath, 'doctrine:mapping:import', bundleName, entitiesFormat], 'descr': 'Creating partials entities'},
	{'cmd': [consolePath, 'doctrine:generate:entities', bundleName], 'descr': 'Creating complete entities'}
]
crudCmd = {'cmd': [consolePath, 'doctrine:generate:crud', '--no-interaction', '--entity=%s', '--route-prefix=%s', '--with-write', '--format=' + entitiesFormat, '--overwrite'], 'descr': 'Creating CRUD for entity %s'}

# Which columns may be used by toString method in entity? Organize them by priority
toStringColumns = ['title', 'name', 'nom', 'titre']

# The toString method which will be inserted in the entity
toStringTemplate = """
    /**
     * Custom toString method made by entitiesml.py
     */
    public function __toString()
    {{
        return $this->{column};
    }}
}}
"""

# Running core commands
print colorize('Running core commands:', 'blue', bold = True)

if not os.path.exists(basePath + os.sep + 'src' + os.sep + namespace):
	for cmd in coreCmds:
		try:
			print '->', cmd['descr']
			subprocess.check_output(cmd['cmd'])
		except Exception, e:
			print colorize(e, 'red')
			sys.exit(0)
else:
	print colorize('\r\nBundle already exists, now generating CRUD.', 'blue')

# Foreach entity we generate a crud via app/console
print '\r\n', colorize('Generating crud for each entity:', 'blue', bold = True)

entitiesList = glob.glob(basePath + os.sep + 'src' + os.sep + namespace + os.sep + 'Entity' + os.sep + '*.php')
for filename in entitiesList:
	entityName = os.path.basename(os.path.splitext(filename)[0])
	try:
		print '->', crudCmd['descr'] % entityName
		subprocess.check_output(' '.join(crudCmd['cmd']) % (bundleName + ':' + entityName, '/%s' % entityName.lower()), shell=True)
	except Exception, e:
		print colorize('Fatal error, exiting:', 'red')
		print colorize(e, 'red')
		sys.exit(0)

# Insert the toString method in the entities
def getDefaultColumn(filename):
	line = 'private $%s;'
	with open(filename) as f:
		content = f.read()
		for item in toStringColumns:
			if line % item in content:
				return item
	return False

if not args.no_ts:
	for entityFile in entitiesList:
		column = getDefaultColumn(entityFile)
		if not column:
			print colorize('No known column found, skipping insertion of toString() method', 'red')
			continue;
		with open(entityFile, 'rb+') as f:
			f.seek(-2, os.SEEK_END)
			f.write(toStringTemplate.format(column=column))
	print colorize('\r\nAll toString methods generated.', 'green')

print colorize('\r\nAll done, thanks for watching, now let\'s go back to work!', 'green')
print colorize('Remember, you can always rollback with "entitiesmk --bundle-name %s --rollback"' % bundleName, 'yellow')