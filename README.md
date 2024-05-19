# Allegro bulk offer editor
A library for Allegro fhat allows for bulk edits to offers on Allegro by writing custom python code that is executed on each selected offer, uses the allegro API.

# Install
To use you are going to need python and some libraries

* json
* http.server
* webbrowser
* time
* requests
* typing
* os
* datetime
* importlib.util
* shutil

if you heave pip you can run `dependeces.bat` to install them all at once

get python here:
https://www.python.org/downloads/

and pip here:
https://pypi.org/project/pip/

# Usage
* Clone or download repository
* make sure dependencies are installed
* To start using this library first you need to provide api keys.
    go to `data\settings.json` and id's and secret's for Allegro and Allegro_sandbox environments
    get or crate keys at:
    https://developer.allegro.pl
* follow instructions in `example_use.ipynb` to get how to use this library

# Features

* Pick offers to be edited by several methods mentioned in `example_use.ipynb`

* This library allows you to write custom python code that  will be run for each offers, check out  `patterns\example` to se what your script must include



* On top of that full backup functionally is included, you can save and load offers

* Interfaces web,and cmd are planed for the feature

# Contributions

All contributions, issues, and messages are welcome! If you aren't sure about something or have any questions please reach out to me.

