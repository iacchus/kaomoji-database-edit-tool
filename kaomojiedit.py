#!/usr/bin/env python3

from sys import argv

import os
import random
import time

import click

from kaomoji import Kaomoji
from kaomoji import KaomojiDB

def backup_db(db: KaomojiDB):

    timestamp = time.time()
    backup_filename = "{filename}.{timestamp}.bkp".format(filename=db.filename,
                                                          timestamp=timestamp)
    backup = KaomojiDB(filename=db.filename)
    backup.write(filename=backup_filename)

# KAOMOJIDB = KaomojiDB()

def open_database(database_filename):

    #global KAOMOJIDB

    if os.path.isfile(database_filename):
        return KaomojiDB(filename=database_filename)

    return None


@click.group()
def cli():
    pass


###############################################################################
# add                                                                         #
###############################################################################

@cli.command()
@click.option("-f", "--database", "database_filename",
              default="kaomoji.tsv",
              help="Kaomoji database")
@click.option("-k", "--kaomoji", "kaomoji",
              prompt="Kaomoji to add",
              help="Kaomoji database to add; use - to read from STDIN.")
@click.option("--keywords",
              prompt="Keywords, comma-separated",
              help="Comma-separated list of keywords to add to this kaomoji.")
def add(database_filename, kaomoji, keywords):
    """Adds the selected kaomoji from the selected database"""

    kaomojidb = open_database(database_filename=database_filename)


###############################################################################
# rm                                                                          #
###############################################################################

@cli.command()
@click.option("-f", "--database", "database_filename",
              default="kaomoji.tsv",
              help="Kaomoji database")
@click.option("-k", "--kaomoji", "kaomoji",
              prompt="Kaomoji to add",
              help="Kaomoji database to add; use - to read from STDIN.")
def rm(database, kaomoji=None):
    """Removes the selected kaomoji from the selected database"""

    kaomojidb = open_database(database_filename=database_filename)


###############################################################################
# kwadd                                                                       #
###############################################################################

@cli.command()
@click.option("-f", "--database", "database_filename",
              default="kaomoji.tsv",
              help="Kaomoji database")
@click.option("-k", "--kaomoji", "kaomoji",
              prompt="Kaomoji to add",
              help="Kaomoji database to add; use - to read from STDIN.")
@click.option("--keywords",
              prompt="Keywords (comma-separated)",
              help="Comma-separated list of keywords.")
def kwadd(database_filename, kaomoji, keywords):
    """Add a comma-separated list of keywords to the selected kaomoji at the
    selected database.
    """

    kaomojidb = open_database(database_filename=database_filename)


###############################################################################
# kwrm                                                                        #
###############################################################################

@cli.command()
@click.option("-f", "--database", "database_filename",
              default="kaomoji.tsv",
              help="Kaomoji database")
@click.option("-k", "--kaomoji", "kaomoji",
              prompt="Kaomoji to add",
              help="Kaomoji database to add; use - to read from STDIN.")
@click.option("-w", "--keywords", "keywords",
              prompt="Keywords (comma-separated)",
              help="Comma-separated list of keywords.")
def kwrm(database_filename, kaomoji, keywords):
    """Removes a comma-separated list of keywords to the selected kaomoji at
    the selected database.
    """

    kaomojidb = open_database(database_filename=database_filename)

if __name__ == "__main__":
    cli()