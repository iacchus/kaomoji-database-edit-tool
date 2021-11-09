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

keywords_add_option = click.option(
    "-a", "--add", "keywords_add",
    default=None,
    multiple=True,
    #prompt="Keywords to add, comma-separated",  # this should go inside function
    help = "Comma-separated or option-separated list of keywords to add.")

keywords_remove_option = click.option(
    "-x", "--rm", "keywords_remove",
    default=None,
    multiple=True,
    #prompt="Keywords to remove, comma-separated",  # this should go inside function
    help="Comma-separated or option-separated list of keywords to remove.")

database_filename_option = click.option(
    "-f", "--database", "database_filename",
    default=None,
    help="Kaomoji database file name.")

kaomoji_option = click.option(
    "-k", "--kaomoji", "kaomoji",
    default=None,
    prompt="Kaomoji",
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
    print(kaomoji)


###############################################################################
# edit                                                                        #
###############################################################################
@cli.command()
@database_filename_option
@kaomoji_option
@keywords_add_option
@keywords_remove_option
def edit(database_filename, kaomoji, keywords_add, keywords_rm):
    """Edits the selected kaomoji, adding or removing keywords"""

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
    """Adds a comma-separated list of keywords to the selected kaomoji at the
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