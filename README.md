# ForMOM DB Rebuilder
*command line utility*

![20Week_DBRebuild](https://user-images.githubusercontent.com/49537988/178081051-e70ae0e2-faeb-45b7-9502-6a4190c1dbf1.png)

This program takes a raw sqlite3 database from FIA Datamart and re-organizes it so that it can be run through FVS. 
We have it setup for New Jersey, but it is configurable for other states - there are example configs for MD and WY.
<!-- Check out the [wiki page](https://github.com/New-Jersey-Forest-Service/ForMOM/wiki/FVS#inputs) for more information on running it. -->

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
**Goal**: Process the New Jersey database from FIA datamart.

First, download the raw file. We fill in the DB_FILEPATH, DB_NAME, and INV_YEARS.
The split dict is a little complicated to explain succicently, so we'll build it up
through this example.

```python
# DBRebuild_Config.py
DB_FILEPATH = './FIADB_NJ.db' # <- Change this on your machine
DB_NAME = 'FIADB_NJ.db'
INV_YEARS = [2015, 2016, 2017, 2018, 2019, 2020]
COUNTY_SPLIT_DICT = { }
```
Right now, the split dict is empty and there's no splitting.
We get this output:
```
Checking for large stands
 > [[ Warning ]]
 >      Stand IDs 167 have 3000+ entries in FVS_TREEINIT_PLOT.
 >      Consider splitting up by county codes
 >
 > [[ Info ]]
 > County distribution for 167
 >    1 | 800
 >    5 | 1998
 >    7 | 86
 >   11 | 355
 >   15 | 125
 >   23 | 44
 >   25 | 153
 >   29 | 1604
 >  tot | 5165
 >
```
The forest type 167 has more than 5165 entries, and so will not be processed by FVS.
So, we split up 167 into two forest types, '167N' and '167S' for 167 north and 167 south.
For 167N, we want to use counties 23, 25, 29, 1 and for 167S we want to use counties
5, 7, 15, 11, 9. So, '167' is the base forest-type that gets split
```python
COUNTY_SPLIT_DICT = {
    '167': {}
}
```
and we'll split it into two sub forest-types
```python
COUNTY_SPLIT_DICT = {
    '167': {
        '167N': [],
        '167S': []
    }
}
```
and into each list, we put the counties we want
```python
COUNTY_SPLIT_DICT = {
    '167': {
        '167N': [23, 25, 29, 1],
        '167S': [5, 7, 15, 11, 9]
    }
}
```
Running this, it works. Note, we can name the forest types whatever we wanted, 
we can split more than 2 ways, and order doesn't matter.
For wyoming, this is an example COUNTY_SPLIT_DICT
```python
COUNTY_SPLIT_DICT = {
	'268': {
		'268A': [3, 7, 13, 19, 23, 25, 29],
		'268B': [33, 35, 39]
	},
	'266': {
		'266A': [1, 3, 7, 13, 19, 23],
		'266B': [29, 33, 35],
		'266C': [39]
	},
	'281': {
		'281A': [1, 3, 7, 13, 23],
		'281C': [29],
		'281B': [33, 35, 19],
		'281D': [39]
	}
}
```


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

Also, I didn't realize you can actually do static type checking (mypy) until like a week
ago, so the type hints were meant for my IDE to give autocomplete. If you'd like,
learn mypy, but the scripts work so I never bothered.





