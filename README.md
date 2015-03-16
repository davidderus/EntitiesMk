EntitiesMk
==========

Python script to auto-generate a Symfony 2 bundle and all its components (Entities, Forms, Templates…) in one command-line.

## Introduction

This tool aims to speed up Symfony 2 entities, forms and crud setup by providing simple command line .

## Dependencies

No specifics packages required, you just need a fresh Symfony 2 installation, with a working connexion to a populated database (like one from a MySQLWorkbench generation).

You also need **Python 2.7**.

## Installation

Download `entitiesmk.py` to your Symfony installation.
You may also copy the file to */usr/local/bin* without its extension and chmod +x it, like below:
```shell
cp entitiesmk.py /usr/local/bin/entitiesmk
chmod +x /usr/local/bin/entitiesmk
```     
and then run this in a Symfony project
```shell
entitiesmk [...]
```

## Usage

Run the following command in your terminal :
```shell
python entitiesmk.py --bundle-name AcmeDemoBundle
```

Yes, that's all.

## Optionnal parameters

You can also provide optionnal parameters like:
 
`--symfony`
Custom path to a Symfony installation. By default the current working dir is used.

`--format`
A specific format used to generate database description and other things. By default it's *annotation*.

`--no-ts`
By default, EntitiesMk cleverly inserts a __toString method to your entities. This way, no __toString missing error.
But if you don't like this comportment, you can desactivate it with this parameter.

`--rollback`
If you've done an error or want to try again, you can use the rollback parameter.
Be careful, all uncommited changes will be lost. And by the way, this feature requires an initialized **git** repository.
