#!/usr/bin/env python3

from sys import argv

import os
import random
import time

import click
import toml

from kaomoji import Kaomoji
from kaomoji import KaomojiDB

from kaomoji import KaomojiDBKaomojiExists
from kaomoji import KaomojiDBKaomojiDoesntExist


# def get_user_config_file(filename=USER_CONFIG_FILE):
def get_user_config_file(filename):

    config_file = os.path.expanduser(filename)

    if os.path.isfile(config_file):
        return toml.load(config_file)

    return {}

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


DEFAULT_CONFIG = {
    'database_filename': './emoticons.tsv',
}

USER_CONFIG_FILE = os.path.expanduser("~/.kaomojiedit")
USER_CONFIG = dict()

CONFIG = DEFAULT_CONFIG  # initialize it with defaults

if os.path.isfile(USER_CONFIG_FILE):
    USER_CONFIG = get_user_config_file(filename=USER_CONFIG_FILE)
    CONFIG.update(USER_CONFIG)


keywords_add_option = click.option(
    "-a", "--add", "keywords_add",
    default=None,
    multiple=True,
    #prompt="Keywords to add, comma-separated",  # this should go inside function
    type=str,
    help = "Comma-separated or option-separated list of keywords to add.")

keywords_remove_option = click.option(
    "-x", "--rm", "keywords_remove",
    default=None,
    multiple=True,
    #prompt="Keywords to remove, comma-separated",  # this should go inside function
    type=str,
    help="Comma-separated or option-separated list of keywords to remove.")

database_filename_option = click.option(
    "-f", "--database", "database_filename",
    default=CONFIG['database_filename'],
    type=str,
    help="Kaomoji database file name.")

kaomoji_code_option = click.option(
    "-k", "--kaomoji", "kaomoji_code",
    #default=None,
    default=click.get_text_stream('stdin').read().strip(),
    #prompt="Kaomoji",
    type=str,
    help="Kaomoji; use - to read from STDIN.")

keywords_option = click.option(
    "-w", "--keywords", "keywords",
    default=None,
    #prompt="Keywords, comma-separated",
    type=str,
    help="Comma-separated list of keywords to change.")

config_filename_option = click.option(
    "-c", "--config", "config_filename",
    default=None,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Kaomoji database file name.")


@click.group()
def cli():
    """Toolchain to edit kaomoji database files.

    Contribute at:

    https://github.com/iacchus/kaomoji-database-edit-tool/
    """
    pass


###############################################################################
# add                                                                         #
###############################################################################
@cli.command()
@database_filename_option
@kaomoji_code_option
@keywords_option
@config_filename_option
def add(database_filename, kaomoji_code, keywords, config_filename):
    """Adds the selected kaomoji to the selected database"""

    if config_filename and os.path.isfile(config_filename):
        user_config = get_user_config_file(filename=USER_CONFIG_FILE)
        CONFIG.update(user_config)

    if database_filename:
        CONFIG.update({'database_filename': database_filename})

    db_filename = CONFIG['database_filename']
    kaomojidb = open_database(database_filename=db_filename)

    if not kaomojidb:
        print("else here!! DATABASE NEEDED")
        exit(1)

    #kaomojidb = open_database(database_filename=database_filename)

    if isinstance(kaomoji_code, str) and kaomoji_code != "":
        new_kaomoji = Kaomoji(code=kaomoji_code, keywords=keywords)

    if kaomojidb:
        backup_db(db=kaomojidb)
    else:
        raise FileNotFoundError

    if not kaomojidb.kaomoji_exists(new_kaomoji):
        print("Adding...")
        print("kaomoji: ", new_kaomoji.code)
        print("keywords: ", new_kaomoji.keywords)
        kaomojidb.add_kaomoji(new_kaomoji)
    else:
        raise KaomojiDBKaomojiExists

    click.echo("Writing db {}".format(kaomojidb.filename))
    kaomojidb.write()


###############################################################################
# edit                                                                        #
###############################################################################
@cli.command()
@database_filename_option
@kaomoji_code_option
@keywords_add_option
@keywords_remove_option
def edit(database_filename, kaomoji_code, keywords_add, keywords_rm):
    """Edits the selected kaomoji, adding or removing keywords"""

    kaomojidb = open_database(database_filename=database_filename)


###############################################################################
# rm                                                                          #
###############################################################################
@cli.command()
@database_filename_option
@kaomoji_code_option
@config_filename_option
def rm(database_filename, kaomoji_code, config_filename):
    """Removes the selected kaomoji from the selected database"""

    if config_filename and os.path.isfile(config_filename):
        user_config = get_user_config_file(filename=USER_CONFIG_FILE)
        CONFIG.update(user_config)

    if database_filename:
        CONFIG.update({'database_filename': database_filename})

    db_filename = CONFIG['database_filename']
    kaomojidb = open_database(database_filename=db_filename)

    if not kaomojidb:
        print("else here!! DATABASE NEEDED")
        exit(1)

    if isinstance(kaomoji_code, str) and kaomoji_code != "":
        #kaomoji_to_remove = Kaomoji(code=kaomoji_code, keywords=keywords)
        kaomoji_to_remove = Kaomoji(code=kaomoji_code)

    if kaomojidb:
        backup_db(db=kaomojidb)
    else:
        raise FileNotFoundError

    if kaomojidb.kaomoji_exists(kaomoji_to_remove):
        print("Removing...")
        print("kaomoji: ", kaomoji_to_remove.code)
        print("keywords: ", kaomoji_to_remove.keywords)
        kaomojidb.remove_kaomoji(kaomoji_to_remove)
    else:
        raise KaomojiDBKaomojiDoesntExist

    click.echo("Writing db {}".format(kaomojidb.filename))
    kaomojidb.write()


###############################################################################
# kwadd                                                                       #
###############################################################################
@cli.command()
@database_filename_option
@kaomoji_code_option
@keywords_option
def kwadd(database_filename, kaomoji_code, keywords):
    """Adds a comma-separated list of keywords to the selected kaomoji at the
    selected database.
    """

    kaomojidb = open_database(database_filename=database_filename)


###############################################################################
# kwrm                                                                        #
###############################################################################
@cli.command()
@database_filename_option
@kaomoji_code_option
@keywords_option
def kwrm(database_filename, kaomoji_code, keywords):
    """Removes a comma-separated list of keywords to the selected kaomoji at
    the selected database.
    """

    kaomojidb = open_database(database_filename=database_filename)


if __name__ == "__main__":

    cli()