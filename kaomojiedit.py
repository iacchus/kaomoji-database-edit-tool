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


def open_database(database_filename):

    if os.path.isfile(database_filename):
        return KaomojiDB(filename=database_filename)

    return None


@click.group()
def cli():
    pass


database_filename_option = click.option(
    "-f", "--database", "database_filename",
    default=None,
    help="Kaomoji database")

kaomoji_option = click.option(
    "-k", "--kaomoji", "kaomoji",
    default=None,
    prompt="Kaomoji to add",
    help="Kaomoji; use - to read from STDIN.")

keywords_option = click.option(
    "-w", "--keywords", "keywords",
    default=None,
    prompt="Keywords, comma-separated",
    help="Comma-separated list of keywords to change.")

###############################################################################
# add                                                                         #
###############################################################################

@cli.command()
@database_filename_option
@kaomoji_option
def add(database_filename, kaomoji, keywords):
    """Adds the selected kaomoji from the selected database"""

    kaomojidb = open_database(database_filename=database_filename)


###############################################################################
# rm                                                                          #
###############################################################################

@cli.command()
@database_filename_option
@kaomoji_option
def rm(database_filename, kaomoji=None):
    """Removes the selected kaomoji from the selected database"""

    kaomojidb = open_database(database_filename=database_filename)


###############################################################################
# kwadd                                                                       #
###############################################################################

@cli.command()
@database_filename_option
@kaomoji_option
@keywords_option
def kwadd(database_filename, kaomoji, keywords):
    """Add a comma-separated list of keywords to the selected kaomoji at the
    selected database.
    """

    kaomojidb = open_database(database_filename=database_filename)


###############################################################################
# kwrm                                                                        #
###############################################################################

@cli.command()
@database_filename_option
@kaomoji_option
@keywords_option
def kwrm(database_filename, kaomoji, keywords):
    """Removes a comma-separated list of keywords to the selected kaomoji at
    the selected database.
    """

    kaomojidb = open_database(database_filename=database_filename)

if __name__ == "__main__":
    cli()