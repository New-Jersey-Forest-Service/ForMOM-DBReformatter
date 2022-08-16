# ForMOM DB Reformatter
*command line utility*

![20Week_DBRebuild](https://user-images.githubusercontent.com/49537988/178081051-e70ae0e2-faeb-45b7-9502-6a4190c1dbf1.png)

This program takes a raw sqlite3 database from FIA Datamart and re-organizes it so that it can be run through FVS. 
We have it setup for New Jersey, but it is configurable for other states - there are example configs for MD and WY.
Check out the [wiki page](https://github.com/New-Jersey-Forest-Service/ForMOM/wiki/FVS#inputs) for more information on running it.

**Credits**: 
The re-organization process was thought of and developed by Lauren and Courtney, with help from Bill.
The automation of it was done by Michael.


# Running
To run the program, execute DBRebuild_Main.py.
As input, it must be given a database straight from FIA Datamart.
To configure the program, 
**DBRebuild_Config.py is the only file you need to edit**.
There are no python dependencies, but Python 3.8+ is recommended.

The config consists of 4 variables
 - **DB_FILEPATH**: The file of the database
 - **DB_NAME**: The name of the database (the name of the file *when it was first downloaded from Datamart*)
 - **INV_YEARS**: A list of relevant years to extract from the FIA data
 - **COUNTY_SPLIT_DICT**: Specifies how to split counties, used for very forest types

## Example
A full example lives on the [ForMOM wiki](https://github.com/New-Jersey-Forest-Service/ForMOM/wiki/FVS#configuring-dbrebuild).
It walks you through processing the NJ Database.


# Contributing

There are a couple kind of annoying datastructures, but this program is
very sequential. The main function in DBRebuild_Main.py gives a very clear
breakdown of steps.

The process this is automating can be found in the sample-scripts folder.
The file HowToBuildThisDatabase_032222.txt describes the process
Lauren and others went through when building the database, and
includes many SQL queries.

The code at the bottom of DBRebuild_StandID.py executes just the id replace
step. DBRebuild_StandID.py has 2 toplevel calls
 - **do_id_replace(cursor, replace_dict)** - Does the ID replacements
 - **get_num_fortypes_by_county(cursor, table, split_dict)** - Generates the dictionary to help report oversized forest types. It takes the split dict into account.

All functions have function comments. To work on this code, I'd recommend understanding
(though not necessary) what the FIA databases look like. There are
[official resources](https://www.fia.fs.fed.us/library/database-documentation/index.php)
but I actually got all my questions answered by the team, and that's probably going to
be the faster route.


## SQL Calls
I'm paramaterizing SQL calls using string replacements, which
is a very bad practice, however the methods provided by sqlite3
in python just weren't working :/. If they work for you that will be
great.

The majority of the SQL calls live in two files, commandblock1.sql
and commandblock2.sql. commandblock1.sql has ``$$INVENTORY_YEARS$$`` as
a placeholder that gets replaced by python via string replacement.
Otherwise, they're just pure blocks of sql that get executed.


## Typing
Most values are typed (function params and returns). Typing helps for some things,
but for the dictionaries, the function comments should help the most.

I didn't realize you can do static type checking until last week, so the type
hints are for my IDE to give me autocomplete. It should pass a checker like
mypy, but the script works so I never bothered.





