'''
This script generates the Replace_ID tables that are needed to swap out
the FIA IDs with stand IDs for FVS.

It will actually modify the database, so there is no need for 
extra csvs, etc.

Note, this script does not create duplicate tables 'IDReplace'

Michael Gorbunov
"FVSStandID.ipynb" by Bill Zipse was used as reference
'''

import sqlite3
import sys
from typing import List, Dict

# TODO: Less magic numbers
#   - [ ] Somehow explain or derive the 7
# TODO: Less magic names
#	- [ ] Use dataclases or attrs classes instead of dicts
# TODO: Better queries
#	- [ ] Rewrite the queries to use cur.executemany()

def parse_as_int_if_valid(float_str: str) -> int:
	try:
		float(float_str)
		return int(float(float_str))
	except:
		return -1


def create_dict_fortype_of_standcn(cur: sqlite3.Cursor, tables: List[str], county_split_dict: Dict[str, Dict[str, List[int]]]):
	# creates a map from for_type (str) -> list of STAND_CN (List[int])
	stand_fortype_map = {}

	fortypes_to_split = list(county_split_dict.keys())

	for table_name in tables:
		query = f'SELECT GROUPS, STAND_CN, COUNTY FROM {table_name}'
		cur.execute(query)

		for row in cur:
			stand_cn = int(row[1])

			str_groups = str(row[0]).split(" ")
			FOR_TYPE_IND = 7
			# This is making a lot of assumptions about the db :(
			for_type = str(str_groups[FOR_TYPE_IND]).split("=")[1]

			# Do the county split
			if for_type in fortypes_to_split:
				county = parse_as_int_if_valid(row[2])
				for_type = county_split_id(for_type, county, str_groups, stand_cn, county_split_dict)

			if for_type not in stand_fortype_map.keys():
				stand_fortype_map[for_type] = [stand_cn]
			elif not stand_cn in stand_fortype_map[for_type]:
				stand_fortype_map[for_type].append(stand_cn)
	
	return stand_fortype_map


def create_dict_fortype_of_standcn_by_county(cur: sqlite3.Cursor, tables: List[str], county_split_dict: Dict[str, Dict[str, List[int]]]):
	'''
	Generates a map associating forest types with counties with stand_cn
	{	
		'167N': {
			1: [4324543, 54234, 243243, ...],
			13: [54353, 35435, 5345345, ...,
			  ...
		},
		'167S': { ... },
			...
	}
	'''
	stand_fortype_by_county = {}

	fortypes_to_split = list(county_split_dict.keys())

	for table_name in tables:
		query = f'SELECT GROUPS, STAND_CN, COUNTY FROM {table_name}'
		cur.execute(query)

		for row in cur:
			stand_cn = int(row[1])

			str_groups = str(row[0]).split(" ")
			FOR_TYPE_IND = 7
			# This is making a lot of assumptions about the db :(
			for_type = str(str_groups[FOR_TYPE_IND]).split("=")[1]

			# Do the county split
			county = parse_as_int_if_valid(row[2])
			if for_type in fortypes_to_split:
				for_type = county_split_id(for_type, county, str_groups, stand_cn, county_split_dict)

			if for_type not in stand_fortype_by_county.keys():
				stand_fortype_by_county[for_type] = {}
			if not county in stand_fortype_by_county[for_type].keys():
				stand_fortype_by_county[for_type][county] = []
			if not stand_cn in stand_fortype_by_county[for_type][county]:
				stand_fortype_by_county[for_type][county].append(stand_cn)
	
	return stand_fortype_by_county


def county_split_id (for_type: str, county: int, str_groups: str, stand_cn: str, county_split_dict: dict) -> str:
	for new_fortype in county_split_dict[for_type].keys():
		if county in county_split_dict[for_type][new_fortype]:
			return new_fortype
	
	# The for loop above is expected to return
	# TODO: Communicate this better
	# print(" > [[ Warning ]]")
	# print(f" > \tFound {for_type} forest type outside of specified counties")
	# print(f" > \tGroups: {str_groups}")
	# print(f" > \tStand CN: {stand_cn}")
	# print(f" > \tCounty: {county}")
	return for_type



def replace_ids_in_table(cur: sqlite3.Cursor, table_name:str, cn_to_fortype_dict: Dict[str, List[int]]) -> None:
	for ind, key in enumerate(list(cn_to_fortype_dict.keys())):
		for_type = key
		stand_cn_list = [str(x) for x in cn_to_fortype_dict[key]]

		query = f'''
			UPDATE {table_name} SET STAND_ID = "{for_type}"
			WHERE STAND_CN IN ({", ".join(stand_cn_list)})
		'''
		cur.execute(query)

	print(f" > Finished ID Replacement for {table_name}")



def get_num_fortypes_by_county(cur: sqlite3.Cursor, table: str, county_split_dict: dict) -> Dict[str, Dict[int, int]]:
	'''
	Returns a breakdown of how many entries exist for each forest type,
	by county.
	{
		'167N': { 1: 432, 2: 54, ... },
		'167S': { ... }
		...
	}
	'''
	county_size_dict = {}
	fortype_by_county_dict = create_dict_fortype_of_standcn_by_county(
		cur,
		['FVS_STANDINIT_PLOT', 'FVS_PLOTINIT_PLOT'],
		county_split_dict
	)

	for ind, for_type in enumerate(list(fortype_by_county_dict.keys())):
		county_size_dict[for_type] = {}

		for county in list(fortype_by_county_dict[for_type].keys()):
			stand_cn_list = [str(x) for x in fortype_by_county_dict[for_type][county]]

			query = f'''
				SELECT COUNT(*) AS AMNT
				FROM {table}
				WHERE STAND_CN IN ({", ".join(stand_cn_list)})
			'''
			cur.execute(query)
			num_trees = 0
			for row in cur:
				num_trees = parse_as_int_if_valid(row[0])
			if num_trees != 0:
				county_size_dict[for_type][county] = num_trees

		if ind % 10 == 0 and ind != 0:
			print(" > Counted counties for 10 forest types")
		

	return county_size_dict


def do_id_replace(cur: sqlite3.Cursor, county_split_dict: dict) -> None:
	# Actual processing
	fortype_dict = create_dict_fortype_of_standcn(
		cur, 
		["FVS_STANDINIT_PLOT", "FVS_PLOTINIT_PLOT"],
		county_split_dict
	)

	# Now do replacements
	replace_ids_in_table(cur, "FVS_PLOTINIT_PLOT", fortype_dict)
	replace_ids_in_table(cur, "FVS_STANDINIT_PLOT", fortype_dict)
	replace_ids_in_table(cur, "FVS_TREEINIT_PLOT", fortype_dict)

	replace_ids_in_table(cur, "FVS_PLOTINIT_PLOT_INVYEARST", fortype_dict)
	replace_ids_in_table(cur, "FVS_STANDINIT_PLOT_INVYEARST", fortype_dict)
	replace_ids_in_table(cur, "FVS_TREEINIT_PLOT_INVYEARST", fortype_dict)

	print(" > Finished ID Replace")


if __name__ == '__main__':
	DB_PATH = "./FIADB_NJ.db"
	db_connection = sqlite3.connect(DB_PATH)
	cur = db_connection.cursor()

	print("WARNING: This file only runs the ID replacement steps.")
	print("\tIt is automatically run from the main file, so you")
	print("\tdo not need to run this seperately.")
	print("\tIt is meant to be run by developers of the program.")
	print()

	usr_input = str(input("Do you still wish to continue? (y/n)"))
	print()

	if (usr_input.strip().lower() != 'y'):
		print("Ok, exiting")
		sys.exit(0)
	else:
		print("Ok, continuing")


	do_id_replace(cur, {})

	db_connection.commit()
	db_connection.close()


