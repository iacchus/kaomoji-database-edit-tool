# Kaomoji Database Edit Tool

Quickly add and categorize kaomojis in a database.

Python lib (ready) and tool (soon...) to edit kaomoji database.

Features:

* easily add new kaomoji to the database
* easily add ou remove new keywords

## User config file:

You can have a user configuration file at `~/.kaomojiedit`. The file has `toml`
format. Current options:

### `~/.kaomojiedit` config file
```
database_filename = "emoticons.tsv"  # can be a path relative to current
                                     # directory or absolute; ~ is expanded
                                     # to $HOME
                                     # default database file to edit
```
