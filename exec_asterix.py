#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 19:49:31 2024

@author: rodrigo
"""


'''
 IMPORTANT NOTES: 
  1)  All filenames are examples
  2)  Decoding (unless otherwise specified) is based on the creation of an object containing the list of 
    all decoded messages in order and with the corresponding items according to each UAP. It is useful and 
    manageable for not very large amounts of data (<= 250.000 messages MAX. at once).
    For larger amounts of data it is recommended to split the main file into smaller ones (ast.split_file()), 
    or use the methods that decode from file to file without saving in the intermediate process. 
  3)  Methods using the "messages_asterix" variable use the object to extract the required data 
'''



#%%###########################################################################
# Set error log configuration manually

######################################
###  [0] Error log configuration  ####
######################################

import pyasterix as ast

ast.set_log()



#%%###########################################################################
# Save data on file (same name as origin with "_HEX.txt" at the end) if 
# "save_file" is true

#################################
### [1] .ast Data extraction ####
#################################

import pyasterix as ast


sample_filename = 'ADSB.ast'
message_list = []
save_file = True

ast.ast_to_hex(sample_filename, message_list, save_file)


####
# Split huge files into equal lines number files
#

import pyasterix as ast


input_file = 'ADSB_HEX.txt'
number_lines = 250000  
path = 'test/'
prefix = 'ADSB_HEX_part'

ast.split_file(input_file, prefix, number_lines, path)



#%%###########################################################################
# Decode one message 

#####################################
###  [2] Decode ASTERIX message  ####
#####################################

import pyasterix as ast


message = ('150063F71B7B6BD3A70414D70101000D95011CFAA6FDAE330E7D5334FED7199A342' +
           '1083840AF3840BF08C40FF315A0120336020A40020A063F2E683840EA242173C75E2' +
           '000C3200818D001F7C35940070517070303050703031C170907C40858000000')

message_asterix = ast.decode_message(message)



#%%###########################################################################
# Decoded into variable object type Category21 or Category48 (more categories will 
# be added as they are developed.)

###############################################
###  [3.1] Decode ASTERIX messages (file)  ####
###############################################

import pyasterix as ast


input_file = 'ADSB_HEX.txt' #CAT21
category = 21

messages_asterix = ast.decode_file(input_file, category)


####
# From file directly decoded to JSON
#

##############################################################
###  [3.2] Decode ASTERIX messages list file to JSON file  ###
##############################################################

import pyasterix as ast


input_file = 'ADSB_HEX.txt'
output_file = 'ADSB_21.json'

ast.decode_file_to_json(input_file, output_file)


####
# From file directly decoded to csv
#

###############################################################
###  [3.3] Decode ASTERIX messages list (file) to csv file  ###
###############################################################

import pyasterix as ast


input_file = 'ADSB_HEX.txt'
output_file = 'ADSB_21.csv'

ast.decode_file_to_csv(input_file, output_file)


####
# From variable to csv
#

############################################################
###  [3.4] Dump ASTERIX messages list (var) to csv file  ###
############################################################

import pyasterix as ast


output_file = 'ADSB_21.csv'

ast.var_to_csv(output_file, messages_asterix)



#%%###########################################################################
# Dump object messages (transformed to dict) to JSON file 

##################################
#####  [4] Dump all to JSON  #####
##################################

import pyasterix as ast


output_file = 'ADSB_21.json'

ast.dump_all_to_json(output_file, messages_asterix)
#pyasterix.dump_all_to_json_bk(file1, messages_asterix)



#%%###########################################################################
# Dump object messages (transformed to dict) to reloadable JSON file 

########################################
###  [5] Dump and load JSONPICKLE  ####
########################################

import pyasterix as ast


output_file = 'ADSB_21.json'

ast.dump_to_jsonpickle(output_file, messages_asterix)


####
# Load object
#

import pyasterix as ast


input_file = 'ADSB_21.json'

messages_asterix_2 = ast.load_from_jsonpickle(input_file)



#%%###########################################################################
# Dump to csv from JSON (JSON from [4])
# Note 1: check [3.3] for file-csv conversion
# Note 2: check [3.4] for var-csv conversion

#######################
#####   [6] CSV   #####
#######################

import pyasterix as ast


input_file = 'ADSB_21.json'
output_file = 'ADSB_21.csv'

ast.dump_to_csv(input_file, output_file)



#%%###########################################################################
# Dump to MongoDB (server with mongod required)

##########################
#####  [7] MongoDB  ######
##########################

import pyasterix as ast
 

ast.dump_to_mongodb(messages_asterix)



#%%###########################################################################
# Dump to SQLite database 

###########################
##### [8] SQLite DB #######
###########################

import pyasterix as ast


output_file = 'ADSB_21.db'

ast.dump_to_sqlite(output_file, messages_asterix)



#%%###########################################################################
# Save one message (all its blocks) into human format on a variable  
   
        
###################################
##### [9] Message to string #######
###################################

import pyasterix as ast


info_message = ast.message_str(messages_asterix.messages[0]) #First message of the list

print(info_message)



#%%###########################################################################
# Dump choosen items of message into txt file (CAT21)

######################################
#####  [10] CAT21 Items to TXT  ######
######################################

import pyasterix as ast


output_file = 'ADSB_HEX_items.txt'
items_to_save = ["item080", "item131", "item140", "item073",
                 "item170", "item020"]  

ast.dump_items_txt(output_file, messages_asterix, items_to_save)
    

####
# Read de CSV to check if it has been dumped correctly
#

import pandas as pd


input_file = 'ADSB_HEX_items.txt'

data = pd.read_csv(input_file, delimiter='\t', engine='python')



#%%###########################################################################
#  Dump choosen items of message (only hex BDS)  into txt file (CAT48)

####################################
#####  [11] CAT48 BDS to TXT  ######
####################################
 
import pyasterix as ast


output_file = 'MODO_S_HEX_items.txt'

ast.dump_bds_txt(output_file, messages_asterix)


####
# Read de CSV to check if it has been dumped correctly
#

import pandas as pd


input_file = 'MODO_S_HEX_items.txt'

data = pd.read_csv(input_file, delimiter='\t', engine='python')



#%%###########################################################################
# Dump BDS category decoded into txt file (CAT48)

###################################
#####  [12] TXT BDS Category  #####
###################################
 
import pyasterix as ast


input_file = 'MODO_S_HEX_items.txt'
output_file = 'MODO_S_HEX_items_BDS50.txt'
bds_type = 'BDS50'

ast.dump_bds_cat_txt(input_file, output_file, bds_type)

####
# Read de CSV to check if it has been dumped correctly
#

import pandas as pd


input_file = 'MODO_S_HEX_items_BDS50.txt'

data = pd.read_csv(input_file, delimiter='\t', engine='python')



#%%###########################################################################
# Merge on csv file CAT21 items with BDS50 and BDS60 decoded data, given a 
# max. deviation based on time (s)

####################################################
#####  [13] Merge items CAT21 and BDS50 BDS60  #####
####################################################

import pyasterix as ast


fileCAT21 = 'ADSB_HEX_items.txt'
fileBDS50 = 'MODO_S_HEX_items_BDS50.txt'
fileBDS60 = 'MODO_S_HEX_items_BDS60.txt'

output_file = 'merge_items.csv'
max_dev = 5

ast.merge_data(fileCAT21, fileBDS50, fileBDS60, output_file, max_dev)



#%%###########################################################################
# Calculate dataframe with ASTERIX and ERA5 meteo data (temperature and 
# wind velocity)

########################################
#####  [14] Calculate meteo index  #####
########################################

import pyasterix as ast


input_file = 'merge_items.csv'
output_file = 'meteo_info.csv'
local_meteo_grid = 'gridinfo/meteo/era5-zarr'

ast.calculate_meteo(input_file, output_file, local_meteo_grid)


