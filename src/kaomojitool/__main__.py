#!/usr/bin/env python3

from sys import argv

import os
import random
import time

import click
import toml

# from kaomojitool.kaomoji import Kaomoji
# from kaomojitool.kaomoji import KaomojiDB
#
# from kaomojitool.kaomoji import KaomojiDBKaomojiExists
# from kaomojitool.kaomoji import KaomojiDBKaomojiDoesntExist
from .kaomoji import Kaomoji
from .kaomoji import KaomojiDB

from .kaomoji import KaomojiDBKaomojiExists
from .kaomoji import KaomojiDBKaomojiDoesntExist

class KaomojiToolNoDatabase(Exception):
    description="Kaomoji edit tool couldn't open database"
    def __init__(self, *args, **kwargs):
        super().__init__(self.description, *args, **kwargs)

DEFAULT_CONFIG = {
    'database_filename': './emoticons.tsv',
}

USER_CONFIG_FILE = os.path.expanduser("~/.kaomojitool")
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
    default=None,
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

other_database_filename_option = click.option(
    "-o", "--other-database", "other_database_filename",
    default=None,
    type=str,
    help="Kaomoji database file name to compare with the default.")

diff_type_option = click.option(
    "-t", "--diff-type", "diff_type",
    default="additional",
    #prompt="Keywords, comma-separated",
    type=click.Choice(["additional", "difference", "exclusive",
                       "intersection"], case_sensitive=False),
    help="Comma-separated list of keywords to change.")

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

    print("Backing up the database '{}'...".format(db_filename))
    backup_db(db=kaomojidb)

    kaomoji_add_list: list = list()

    if kaomoji_code:
        new_kaomoji = Kaomoji(code=kaomoji_code, keywords=keywords)
        kaomoji_add_list.append(new_kaomoji)
    else:  # read from stdin
        stdin = click.get_text_stream('stdin')

        for line in stdin.readlines():
            kaomoji, *args = line.strip().split('\t')
            kaomoji_code = kaomoji.strip()

            if not kaomoji_code:
                continue  # line empty or empty first element

            keywords = [] if not args else args[0]

            new_kaomoji = Kaomoji(code=kaomoji_code, keywords=keywords)
            kaomoji_add_list.append(new_kaomoji)

    for kaomoji in kaomoji_add_list:

        db_kaomoji = kaomojidb.get_kaomoji(kaomoji)  # reference or None

        if db_kaomoji and kaomoji.keywords:
            print("Kaomoji already exists! Updating keywords..")
            db_kaomoji.add_keywords(keywords)
        elif not db_kaomoji:
            print("New kaomoji! Adding...")
            db_kaomoji = kaomojidb.add_kaomoji(kaomoji)  # returns reference

        print("kaomoji:", db_kaomoji.code)
        print("keywords:", db_kaomoji.keywords)

    print("Writing db", kaomojidb.filename)
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
def edit(database_filename, kaomoji_code, keywords_add, keywords_remove,
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
    keywords_to_remove = ",".join(keywords_remove)

    print(keywords_to_remove)
    if not kaomojidb.get_kaomoji(by_entity=kaomoji_code):
        print("New kaomoji! Adding it do database...")
        new_kaomoji = kaomojidb.add_kaomoji(Kaomoji(code=kaomoji_code))
    else:
        print("Kaomoji already exists! Removing keywords from it...")

    edit_kaomoji = kaomojidb.get_kaomoji(by_entity=kaomoji_code)
    if keywords_to_remove:
        edit_kaomoji.remove_keywords(keywords=keywords_to_remove)
    if keywords_to_add:
        edit_kaomoji.add_keywords(keywords=keywords_to_add)

    print("Backing up the database...")
    backup_db(db=kaomojidb)

    print("Editing...")
    print("kaomoji:", edit_kaomoji.code)
    print("keywords:", edit_kaomoji.keywords)
    kaomojidb.update_kaomoji(edit_kaomoji)

    print("Writing db", kaomojidb.filename)
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
        print("kaomoji:", kaomoji_to_remove.code)
        print("keywords:", kaomoji_to_remove.keywords)
        kaomojidb.remove_kaomoji(kaomoji_to_remove)
    else:
        raise KaomojiDBKaomojiDoesntExist

    print("Writing db", kaomojidb.filename)
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
    print("kaomoji:", edit_kaomoji.code)
    print("keywords:", edit_kaomoji.keywords)
    kaomojidb.update_kaomoji(edit_kaomoji)

    print("Writing db", kaomojidb.filename)
    kaomojidb.write()


###############################################################################
# kwrm                                                                        #
###############################################################################
@cli.command()
@database_filename_option
@kaomoji_code_option
@config_filename_option
@keywords_option
def kwrm(database_filename, kaomoji_code, keywords, config_filename):
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
    print("kaomoji:", edit_kaomoji.code)
    print("keywords:", edit_kaomoji.keywords)
    kaomojidb.update_kaomoji(edit_kaomoji)

    print("Writing db", kaomojidb.filename)
    kaomojidb.write()


###############################################################################
# diff                                                                        #
###############################################################################
@cli.command()
@database_filename_option
@other_database_filename_option
@diff_type_option
@config_filename_option
def diff(database_filename, other_database_filename, diff_type,
         config_filename):
    """Compare two databases and logs the difference between them."""

    if config_filename and os.path.isfile(config_filename):
        user_config = get_user_config_file(filename=USER_CONFIG_FILE)
        CONFIG.update(user_config)

    if database_filename:
        CONFIG.update({'database_filename': database_filename})

    db_filename = CONFIG['database_filename']
    kaomoji_db = open_database(database_filename=db_filename)
    other_db = open_database(database_filename=other_database_filename)

    if not kaomoji_db or not other_db:
        raise KaomojiToolNoDatabase

    diff_dict = kaomoji_db.compare(other=other_db, diff_type=diff_type)
    print(diff_dict)

    # TODO: TAKE SHA256, FORMAT FOR KaomojiDB, WRITE


###############################################################################
# dbstatus                                                                    #
###############################################################################
@cli.command()
@database_filename_option
@config_filename_option
def dbstatus(database_filename, config_filename):
    """Show data from the database."""

    if config_filename and os.path.isfile(config_filename):
        user_config = get_user_config_file(filename=USER_CONFIG_FILE)
        CONFIG.update(user_config)

    if database_filename:
        CONFIG.update({'database_filename': database_filename})

    db_filename = CONFIG['database_filename']
    kaomoji_db = open_database(database_filename=db_filename)

    if not kaomoji_db:
        raise KaomojiToolNoDatabase

    number_of_kaomoji = len(kaomoji_db.kaomojis)

    print("database file:", db_filename)
    print("number of kaomojis:", number_of_kaomoji)


if __name__ == "__main__":

    cli()
