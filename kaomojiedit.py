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

class KaomojiToolNoDatabase(Exception):
    description="Kaomoji edit tool couldn't open database"
    def __init__(self, *args, **kwargs):
        super().__init__(self.description, *args, **kwargs)

DEFAULT_CONFIG = {
    'database_filename': './emoticons.tsv',
}

USER_CONFIG_FILE = os.path.expanduser("~/.kaomojiedit")
USER_CONFIG: dict

CONFIG = DEFAULT_CONFIG  # initialize it with defaults

def get_user_config_file(filename):

    config_file = os.path.expanduser(filename)

    if os.path.isfile(config_file):
        return toml.load(config_file)

    return DEFAULT_CONFIG

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


USER_CONFIG = dict()

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
        raise KaomojiToolNoDatabase

    if kaomoji_code:
            new_kaomoji = Kaomoji(code=kaomoji_code, keywords=keywords)

    if not kaomojidb.kaomoji_exists(new_kaomoji):
        print("Backing up the database...")
        backup_db(db=kaomojidb)

        print("Adding...")
        print("kaomoji: ", new_kaomoji.code)
        print("keywords: ", new_kaomoji.keywords)
        kaomojidb.add_kaomoji(new_kaomoji)
    else:
        raise KaomojiDBKaomojiExists

    print("Writing db ", kaomojidb.filename)
    kaomojidb.write()


###############################################################################
# edit                                                                        #
###############################################################################
@cli.command()
@database_filename_option
@kaomoji_code_option
@keywords_add_option
@keywords_remove_option
@config_filename_option
def edit(database_filename, kaomoji_code, keywords_add, keywords_rm,
         config_filename):
    """Edits the selected kaomoji to the selected database, adding or removing
    keywords.
    """

    if config_filename and os.path.isfile(config_filename):
        user_config = get_user_config_file(filename=USER_CONFIG_FILE)
        CONFIG.update(user_config)

    if database_filename:  # command-line option have preemptiness
        CONFIG.update({'database_filename': database_filename})

    db_filename = CONFIG['database_filename']
    kaomojidb = open_database(database_filename=db_filename)

    if not kaomojidb:
        raise KaomojiToolNoDatabase

    keywords_to_add = ",".join(keywords_add)  # adding will have preemptiness
    keywords_to_rm = ",".join(keywords_rm)

    if not kaomojidb.get_kaomoji(by_entity=kaomoji_code):
        print("New kaomoji! Adding it do database...")
        # new_kaomoji = Kaomoji(code=kaomoji_code, keywords=keywords)
        new_kaomoji = Kaomoji(code=kaomoji_code)
        kaomojidb.add_kaomoji(kaomoji=new_kaomoji)
    else:
        print("Kaomoji already exists! Removing keywords from it...")

    edit_kaomoji = kaomojidb.get_kaomoji(by_entity=kaomoji_code)
    if not new_kaomoji:
        edit_kaomoji.remove_keywords(keywords=keywords_to_rm)
    edit_kaomoji.add_keywords(keywords=keywords_to_add)

    print("Backing up the database...")
    backup_db(db=kaomojidb)

    print("Editing...")
    print("kaomoji: ", edit_kaomoji.code)
    print("keywords: ", edit_kaomoji.keywords)
    kaomojidb.update_kaomoji(edit_kaomoji)

    print("Writing db ", kaomojidb.filename)
    kaomojidb.write()


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
        raise KaomojiToolNoDatabase

    if  kaomoji_code:
        kaomoji_to_remove = Kaomoji(code=kaomoji_code)

    if kaomojidb.kaomoji_exists(kaomoji_to_remove):
        print("Backing up the database...")
        backup_db(db=kaomojidb)

        print("Removing...")
        print("kaomoji: ", kaomoji_to_remove.code)
        print("keywords: ", kaomoji_to_remove.keywords)
        kaomojidb.remove_kaomoji(kaomoji_to_remove)
    else:
        raise KaomojiDBKaomojiDoesntExist

    print("Writing db ", kaomojidb.filename)
    kaomojidb.write()


###############################################################################
# kwadd                                                                       #
###############################################################################
@cli.command()
@database_filename_option
@kaomoji_code_option
@config_filename_option
@keywords_option
def kwadd(database_filename, kaomoji_code, keywords, config_filename):
    """Add keywords to the selected kaomoji."""

    if config_filename and os.path.isfile(config_filename):
        user_config = get_user_config_file(filename=USER_CONFIG_FILE)
        CONFIG.update(user_config)

    if database_filename:
        CONFIG.update({'database_filename': database_filename})

    db_filename = CONFIG['database_filename']
    kaomojidb = open_database(database_filename=db_filename)

    if not kaomojidb:
        raise KaomojiToolNoDatabase

    if not kaomojidb.get_kaomoji(by_entity=kaomoji_code):
        print("New kaomoji! Adding it do database...")
        new_kaomoji = Kaomoji(code=kaomoji_code, keywords=keywords)
        kaomojidb.add_kaomoji(kaomoji=new_kaomoji)
    else:
        print("Kaomoji already exists! Removing keywords from it...")

    #edit_kaomoji = kaomojidb.get_kaomoji_by_code(code=kaomoji_code)
    edit_kaomoji = kaomojidb.get_kaomoji(by_entity=kaomoji_code)
    edit_kaomoji.add_keywords(keywords=keywords)

    print("Backing up the database...")
    backup_db(db=kaomojidb)

    print("Removing keywords...")
    print("kaomoji: ", edit_kaomoji.code)
    print("keywords: ", edit_kaomoji.keywords)
    kaomojidb.update_kaomoji(edit_kaomoji)

    print("Writing db ", kaomojidb.filename)
    kaomojidb.write()


###############################################################################
# kwrm                                                                        #
###############################################################################
@cli.command()
@database_filename_option
@kaomoji_code_option
@config_filename_option
@keywords_option
def kwadd(database_filename, kaomoji_code, keywords, config_filename):
    """Remove keywords to the selected kaomoji."""

    if config_filename and os.path.isfile(config_filename):
        user_config = get_user_config_file(filename=USER_CONFIG_FILE)
        CONFIG.update(user_config)

    if database_filename:
        CONFIG.update({'database_filename': database_filename})

    db_filename = CONFIG['database_filename']
    kaomojidb = open_database(database_filename=db_filename)

    if not kaomojidb:
        raise KaomojiToolNoDatabase

    if not kaomojidb.get_kaomoji(by_entity=kaomoji_code):
        print("New kaomoji! Adding it do database...")
        new_kaomoji = Kaomoji(code=kaomoji_code, keywords=keywords)
        kaomojidb.add_kaomoji(kaomoji=new_kaomoji)
    else:
        print("Kaomoji already exists! Adding keywords to it...")

    edit_kaomoji = kaomojidb.get_kaomoji(by_entity=kaomoji_code)
    edit_kaomoji.remove_keywords(keywords=keywords)

    print("Backing up the database...")
    backup_db(db=kaomojidb)

    print("Removing keywords...")
    print("kaomoji: ", edit_kaomoji.code)
    print("keywords: ", edit_kaomoji.keywords)
    kaomojidb.update_kaomoji(edit_kaomoji)

    print("Writing db ", kaomojidb.filename)
    kaomojidb.write()


if __name__ == "__main__":

    cli()