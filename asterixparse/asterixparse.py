#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 13:14:20 2024

@author: rodrigo
"""

import csv
import json
import sqlite3
import logging
import codecs
import subprocess
import os

from dataclasses import asdict
from typing import Any, IO
import jsonpickle
from pymongo import MongoClient
from tqdm import tqdm

from .classesASTERIX import classcategory21
from .classesASTERIX import classcategory48
from .classesASTERIX import classmodes
from .classesASTERIX import meteotool



##############################################################################
# Set error log configuration 

################################
###  [0] Log configuration  ####
################################

def set_log(filename: str = 'errors.log'):
    """
    Set error log configuration. It is by default al INFO level. It will
    store the message that has not been able to decode, preceded by de date.
        
    Parameters
    ----------
    filename : str (optional)
        Name of the file to save the errors. Default = 'errors.log'
              
    """
    try:
        # Log format configuration
        log_format = "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s"
        logging.basicConfig(filename=filename, format=log_format, level=logging.ERROR)
        
        # Get the logger object
        #logger = logging.getLogger(__name__)
        
        # Configure date and time format
        date_format = "%Y-%m-%d %H:%M:%S"
        
        # Set up custom formatter to include date and time
        formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
        for handler in logging.root.handlers:
            handler.setFormatter(formatter)
        
        #print(f'\nLog set correctly: {filename}\n')
            
    except Exception as e:
        print(f"\nError setting log file: {e}\n")



##############################################################################
# Convert .ast file to hexadecimal format (Optional: Dump to txt file).

###################################
###  [1] .ast Data extraction  ####
###################################

def ast_to_hex(filename: str, message_list: [], save_file: bool = False):
    """
    Convert .ast file (binary) to hexadecimal format txt file. If optional "save_file" 
    parameter is set to TRUE, data is saved on file (same name as origin with "_HEX.txt" 
    at the end).
        
    Parameters
    ----------
    filename : str
        Name of the file to save hexadecimal messages.
    message_list : list 
        List of the hexadecimal messages.
    save_file : bool (optional)
        Save on file if True. Default = False
    
    """
    #count = 0
    try:
        with open(filename, 'rb') as file1:
            value = " "
            while True:
                message = ""
                cat = file1.read(1).hex().upper()
                if not cat:
                    break
                
                len_message = file1.read(2).hex().upper()
                message = cat + len_message
                len_message_int = int(len_message,16)
                
                for i in range(len_message_int-3):
                    value = file1.read(1).hex()
                    message += value.upper()
    
                #print(message)
                message_list.append(message)
                #count += 1
                #print("CONTROL 2:  |{}|".format(count))
                
                #Code to control number of messages to convert
                #if count > 100:
                #    break
        print('\nFile converted correctly!\n')
            
    except FileNotFoundError:
        print(f"\nFile {filename} not found.\n")
        
    except Exception as e:
        print(f"\nError reading the file: {e}\n")
        
    #i = 0 
    if save_file:
        try:
            file_save = f'{filename[:-4]}_HEX.txt'
            print(file_save)
            with open(file_save, 'w') as file2:
                for line in message_list:
                    file2.write(line + '\n')
                    
                    #Code to control number of messages to store
                    #i += 1
                    #if i > 5000:
                    #    break
            print(f'\nSaved on {file_save}\n')
        except Exception as e:
            print(f"\nError reading the file: {e}\n")


##############################################################################
# Split huge files into equal lines number files

def split_file(input_file, prefix, number_lines = 0, path = os.getcwd()):
    """
    Split huge files into equal lines number files. Useful for large amounts of
    data to be analysed at the same time.
    created files shall have as their name the name entered in the prefix, followed 
    by a number starting with zero and increasing successively as the following files 
    are generated.
    Recommendation: DO NOT decode files larger than 250,000 lines.
        
    Parameters
    ----------
    input_file : str
        Name of the file to read hexadecimal messages. 
    prefix : str 
        Prefix name of generated files.
    number_lines : int  (optional)
        Number of lines per file. Default = 0 (not splitted)
    path : str (optional)
        Path where the generated files will be saved. Default = cwd
    
    """
    try:
        if number_lines != 0:
            before_split = set(os.listdir(path))
            
            subprocess.run(["split", "-l", str(number_lines), input_file, f'{path}{prefix}_', "--numeric-suffixes"])
            
            after_split = set(os.listdir(path))
            
            new_files = after_split - before_split
            print(f"new files: {new_files}\n")
            
            for i in range(0, len(new_files)): 
                old_name = f"{path}{prefix}_{i:02}"
                new_name = f"{path}{prefix}_{i:02}.txt"
                try:
                    os.rename(old_name, new_name)
                except FileNotFoundError:
                    break
        else:
            print("\nNumber lines equal 0, not splitted\n")

    except Exception as e:
        print(f"\nError splitting file: {e}\n")



##############################################################################
# Decode one message and return items values (object).

#####################################
###  [2] Decode ASTERIX message  ####
#####################################

def decode_message(message: str, verbose: bool = True):
    """
    Decode one message in string type from hexadecimal. 
        
    Parameters
    ----------
    message : str
        String containing de ASTERIX message on hexadecimal format. 
    verbose : bool
        Print decode success/failure
        
    Returns
    -------
    message_asterix : AsterixMessage object
        ASTERIX messages object. Its content and fields depend on the message 
        category.
    
    """
    try:
        message_asterix = None
        cat, length, count_octets = get_catlen(message)
        #print("CAT: {} | LEN: {}".format(cat, length))
    
        if cat == 21:
            message_asterix = classcategory21.AsterixMessage(cat, length, message, count_octets)
            message_asterix.add_blocks()
            
        elif cat == 48:
            message_asterix = classcategory48.AsterixMessage(cat, length, message, count_octets)
            message_asterix.add_blocks()
            
        else:
            if verbose:
                print(f"\nCAT{cat} not implemented yet\n")
                
            return None
        
        if verbose:
            print("\nMessage decoded!")
            
        return message_asterix
    
    except Exception as e:
        print(f"\nError decoding message: {e}\n")


##############################################################################
# Get ASTERIX category and length of a message.

def get_catlen(line):
    """
    Gets the category and length of a message. 
        
    Parameters
    ----------
    line : str
        String containing de ASTERIX message on hexadecimal format. 
        
    Returns
    -------
    asterix_cat : int
        ASTERIX message category.
    asterix_len : int
        ASTERIX message length.
    count_octets : int
        Number of hexadecimal octets read.
    
    """
    base = 16
    catlen_format = [1,2]
    message = []
    count_item = 0
    count_octets = 0
    catlen_format = [1,2]
    while count_item < 2:
        message.append(line[count_octets*2:count_octets*2+catlen_format[count_item]*2])
        count_octets += catlen_format[count_item]
        count_item += 1
    
    asterix_cat = int(message[0], base)
    asterix_len = int(message[1], base)
    count_octets = count_item + 1
    return asterix_cat, asterix_len, count_octets



##############################################################################
# Decode file with messages and return items values (object).

####################################################
###  [3.1] Decode ASTERIX messages list (file)  ####
####################################################

def decode_file(filename: str, cat: int):
    """
    Decode file with messages and return items values (object). Decoded into variable
    object type Category21 or Category48 (more categories will be added as they are developed).
        
    Parameters
    ----------
    filename : str
        Name of the file to read hexadecimal messages. 
    cat : int
        Category to be decoded.
        
    Returns
    -------
    messages_asterix : CategoryXX object (XX = category)
        ASTERIX decoded messages list object. Its content depends on the category.      
    
    """
    messages_asterix = None
    if cat == 21:
        messages_asterix = classcategory21.Category21()
    elif cat == 48:
        messages_asterix = classcategory48.Category48()
    else:
        print(f"\nError: CAT{cat} not implemented yet\n")
        return None
    
    try:
        with open(filename, 'r') as file1:
            
            total_lines = sum(1 for line in file1)
            file1.seek(0)

            num_line = 0
            for line in tqdm(file1, total=total_lines, desc="Progress", 
                             unit=" messages"):
        
                asterix_cat, asterix_len, count_octets = get_catlen(line)
                info = line
                if asterix_cat == cat:
                    try:
                        messages_asterix.add_message(
                            asterix_cat, asterix_len, info, count_octets, num_line
                        )
                        #print("Valid CAT and Len")
                    except ValueError as e:
                        print(f"Error: {e}")
                        logging.error(f'Message decoded with error: {line}\n')
                        logging.error(f'Error: {e}\n')
                    except TypeError as e:
                        print(f"\nMessage error: {line} | Error: {e}\n")
                
                    messages_asterix.add_count()
                    num_line += 1
                else:
                    #print("Error: CAT and message not compatible")
                    logging.error(f'Message not decoded: {line}\n')
                    #break   
                
        print("\n\nMessages decoded!\n")   
        
        return messages_asterix
            
    except FileNotFoundError:
        print(f"\nFile {filename} not found.\n")
        
    except Exception as e:
        print(f"\nError reading the file: {e}\n")
    
    
    
##############################################################################
# Decode file with messages on hex and dump results to JSON file without saving 
# it as variable

################################################################
###  [3.2] Decode ASTERIX messages list (file) to JSON file  ###
################################################################

def decode_file_to_json (input_file: str, output_file: str):
    """
    Decode file with messages and dump results to JSON file without saving 
    it as variable.
        
    Parameters
    ----------
    input_file : str
        Name of the file to read hexadecimal messages. 
    output_file : str
        Name of JSON file to dump decoded messages. 
        
    """
    try:
        with open(input_file, 'r') as file1:
            
            with codecs.open(output_file, 'w', encoding='utf-8') as file2:
            
                total_lines = sum(1 for line in file1)
                file1.seek(0)
        
                file2.write('[')
                for line in tqdm(file1, total=total_lines, desc="Progress", unit=" messages"):
                    message = decode_message(line, verbose = False)
                    
                    if message is not None:
                        dump_message_to_json(file2, message)
                    
                file2.seek(-2, 1)
                file2.write('\n]')
                
        print("\nMessages decoded!")   
        print(f'\nDumped object to: {output_file}\n')     
            
    except FileNotFoundError:
        print("\nFile not found.")
        
    except Exception as e:
        print(f"\nError reading the file: {e}\n")



##############################################################################
# Decode file with messages on hex and dump results to csv file without saving 
# it as variable

###############################################################
###  [3.3] Decode ASTERIX messages list (file) to csv file  ###
###############################################################

def decode_file_to_csv(input_file: str, output_file: str):
    """
    Decode file with messages and dump results to csv file without saving 
    it as variable.
        
    Parameters
    ----------
    input_file : str
        Name of the file to read hexadecimal messages. 
    output_file : str
        Name of csv file to dump decoded messages. 
        
    """
    try:         
        j = 0
        data_dict = {}
        first_mess = True
        with open(input_file, 'r') as file1:
            
            with open(output_file, 'w', newline='') as file2:
                
                csv_writer = csv.writer(file2)
                
                total_lines = sum(1 for line in file1)
                file1.seek(0)
        
                for line in tqdm(file1, total=total_lines, desc="Progress", 
                                 unit=" messages"):
                    
                    message_aux = decode_message(line, verbose = False)
                    
                    if message_aux is not None:
                       
                        for j in range(len(message_aux.blocks)):
                            
                            message = message_aux.blocks[j]
                            attribute_items = list(message.__dict__.keys())
                            
                            for item in attribute_items[1:]:
                                value = getattr(message, item)
                                if value.exist: 
                                    data_dict[item] = asdict(value)
                                else:
                                    data_dict[item] = None
                                    
                        json_object = json.dumps(data_dict, indent=8)
                        json_content = json.loads(json_object)
                        if first_mess:
                            csv_writer.writerow(json_content.keys())
                            first_mess = False
                    
                        csv_writer.writerow(json_content.values())
                        data_dict = {}
        print("\nMessages decoded!")   
        print(f'\nDumped object to: {output_file}\n')     

            
    except FileNotFoundError:
        print("\nFile not found.")
        
    except Exception as e:
        print(f"\nError reading the file: {e}\n")



##############################################################################
# Dump "messages_asterix" variable results to csv file

############################################################
###  [3.4] Dump ASTERIX messages list (var) to csv file  ###
############################################################

def var_to_csv(csv_file: str, messages_list: Any):
    """
    Dump decoded CategoryXX object to csv file. (XX = category)
        
    Parameters
    ----------
    csv_file : str
        Name of csv file to dump decoded messages. 
    messages_list : CategoryXX object (XX = category)
        ASTERIX decoded messages list object. Its content depends on the category.
        
    """
    try:
        j = 0
        data_dict = {}
        first_mess = True
            
        with open(csv_file, 'w', newline='') as file1:
                
            csv_writer = csv.writer(file1)
                
            total_lines = messages_list.count
        
            for message_aux in tqdm(messages_list.messages, total=total_lines, 
                             desc="Progress", unit=" messages"):
        
                for j in range(len(message_aux.blocks)):
                            
                    message = message_aux.blocks[j]
                    attribute_items = list(message.__dict__.keys())
                    
                    for item in attribute_items[1:]:
                        value = getattr(message, item)
                        if value.exist: 
                            data_dict[item] = asdict(value)
                        else:
                            data_dict[item] = None
                            
                json_object = json.dumps(data_dict, indent=8)
                json_content = json.loads(json_object)
                if first_mess:
                    csv_writer.writerow(json_content.keys())
                    first_mess = False
            
                csv_writer.writerow(json_content.values())
                data_dict = {}
        print("\nMessages decoded!\n")   
        print(f'\nDumped object to: {csv_file}\n')   
    
    except FileNotFoundError:
        print("\nFile not found.\n")
        
    except Exception as e:
        print(f"\nError writing CSV file: {e}\n")
    


##############################################################################
# Dump object message (transformed to dict) to JSON file 
# Note: separated in two def to be able to add only ONE message on one call
#       (for memory optimization purpose [RAM]).

############################################
#####  [4.1] Dump one message to JSON  #####
############################################

def dump_message_to_json(file: IO, message_blocks: Any):
    """
    Dump decoded MessageAsterix object to JSON file.
    Reminder: Each message can have more than one data block.
        
    Parameters
    ----------
    file : IO
        File descriptor of output JSON file.
    message_blocks : MessageAsterix object
        ASTERIX decoded message object. Its content depends on the category.
        
    """
    data_dict = {}
    #end_block = False
    j = 0
    for j in range(len(message_blocks.blocks)):
        message = message_blocks.blocks[j]
        attribute_items = list(message.__dict__.keys())
        # Iterar sobre los atributos en el orden de declaración
        for item in attribute_items[1:]:
            value = getattr(message, item)
            if value.exist: 
                data_dict[item] = asdict(value)
            else:
                data_dict[item] = None
        #json_object = jsonpickle.encode(data_dict, indent=8)
        json_object = json.dumps(data_dict, indent=8)
        file.write(json_object)
        file.write(',\n')
        data_dict = {}


def dump_all_to_json(filename: str, messages_list: Any):
    """
    Dump decoded CategoryXX object to JSON file.
        
    Parameters
    ----------
    filename : str
        Name of JSON file to dump decoded messages. 
    messages_list : CategoryXX object (XX = category)
        ASTERIX decoded messages list object. Its content depends on the category.
        
    """
    #end_block = False
    #i = 0
    try:
        with codecs.open(filename, 'w', encoding='utf-8') as file1:
            file1.write('[\n')
            
            total_lines = messages_list.count
            for i in tqdm(range(messages_list.count), total=total_lines, 
                          desc="Progress", unit=" messages"):
            #for i in range(messages_list.count):
                dump_message_to_json(file1, messages_list.messages[i])
                
            file1.seek(-2, 1)
            file1.write('\n]')
            
        print(f'\nDumped object to: {filename}\n')
        
    except Exception as e:
        print(f"\nError dumping into the file: {e}\n")
        
        

##############################################################################
# Dump object with all messages (transformed to dict) to JSON file
# Note: to be use directly on asterix object with more that one message decoded.

####################################
#####  [4.2] Dump all to JSON  #####
####################################

def dump_all_to_json_bk(filename: str, messages_list: Any):
    """
    Dump decoded CategoryXX object to JSON file. (Funcionality same as dump_all_to_json;
    internally, the difference is that the former calls the dump process individually
    for each decoded message).
        
    Parameters
    ----------
    filename : str
        Name of JSON file to dump decoded messages. 
    messages_list : CategoryXX object (XX = category)
        ASTERIX decoded messages list object. Its content depends on the category.
        
    """
    data_dict = {}
    i, j = 0, 0
    try:
        with codecs.open(filename, 'w', encoding='utf-8') as file1:
            
            total_lines = messages_list.count
            file1.write('[')
            for i in tqdm(range(messages_list.count), total=total_lines, 
                          desc="Progress", unit=" messages"):
            #for i in range(messages_list.count):
                for j in range(len(messages_list.messages[i].blocks)):
                    
                    print
                    message = messages_list.messages[i].blocks[j]
                    attribute_items = list(message.__dict__.keys())
                    for item in attribute_items[1:]:
                        value = getattr(message, item)
                        if value.exist:  
                            data_dict[item] = asdict(value)
                            #data_dict[item] = recursive_asdict(value)
                        else:
                            data_dict[item] = None
                    #json_object = jsonpickle.encode(data_dict, indent=8)
                    json_object = json.dumps(data_dict, indent=8)
                    file1.write(json_object)
                    file1.write(',\n')
                    data_dict = {}
                    
            file1.seek(-2, 1)
            file1.write('\n]')
            #file1.write(']')
        
        print(f'\nDumped object to: {filename}\n')
        
    except Exception as e:
        print(f"\nError dumping into the file: {e}\n")



##############################################################################
# Dump complex object into JSON file with "jsonpickle" package.
# Note: it can be useful since all the properties and information of 
#       the object can be saved for later load and study.
# IMPORTANT: Usage NOT recommended for variables with more than 10000 elements

##################################
### [5.1] Dump to JSONPICKLE  ####
##################################

def dump_to_jsonpickle(filename: str, messages_list: Any):
    """
    Dump complex object into JSON file with "jsonpickle" package.
    Note: it can be useful since all the properties and information of 
    the object can be saved for later load and study.
    
    IMPORTANT: Usage NOT recommended for variables with more than 10000 elements
        
    Parameters
    ----------
    filename : str
        Name of JSON file to dump decoded messages. 
    messages_list : CategoryXX object (XX = category)
        ASTERIX decoded messages list object. Its content depends on the category.
        
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            json_object = jsonpickle.encode(messages_list, indent=8)
            file.write(json_object)
        print(f'\nDumped object to: {filename}\n')
        
    except Exception as e:
        print(f"\nError dumping into the file: {e}\n")


########################################
### [5.2] Recovery from JSONPICKLE  ####
########################################

def load_from_jsonpickle(filename: str):
    """
    Load complex object from JSON file with "jsonpickle" package.
    Note: it can be useful since all the properties and information of 
    the object can be saved for later load and study.
        
    Parameters
    ----------
    filename : str
        Name of JSON file from which the object is to be loaded
              
    Returns
    -------
    loaded_object : CategoryXX object (XX = category)
        ASTERIX decoded messages list object. Its content depends on the category.  
        
    """
    try:
        with open(filename, 'rb') as file:
            json_serialized = file.read()
            loaded_object = jsonpickle.loads(json_serialized)
        print('\nLoaded!')
        return loaded_object
    
    except Exception as e:
        print(f"\nError dumping into the file: {e}\n")



##############################################################################
# Dump to CSV from JSON file (use JSON from "dump_all_to_json", NOT from jsonpickle)

#######################
#####  [6] CSV  #######
#######################

def dump_to_csv(json_filename: str, csv_filename: str):
    """
    Dump to csv from JSON file (use JSON generated with dump_all_to_json(), NOT 
    from dump_to_jsonpickle()).
        
    Parameters
    ----------
    json_filename : str
        Name of JSON file to read decoded messages. 
    csv_filename : str
        Name of csv file to dump decoded messages. 
        
    """
    try:
        with open(json_filename, 'r') as file1:
            json_content = json.load(file1)
        
        with open(csv_filename, 'w', newline='') as file2:
            # Creat CSV writer object
            csv_writer = csv.writer(file2)
            
            # Write CSV header (based on JSON dict keys)
            csv_writer.writerow(json_content[0].keys())
            
            for mess in json_content:
                # Write data on a row
                csv_writer.writerow(mess.values())
        
        print(f"Dumped object to: {csv_filename}\n")
        
    except Exception as e:
        print(f"Error dumping into the file: {e}\n")



##############################################################################
# Dump all messages (one by one) converted to dict to a MongoDB database

# Start mongo on terminal -->> sudo systemctl start mongod
# Check if it is running correctly -->> sudo systemctl status mongod
# Restart -->> sudo systemctl restart mongod
# Stop -->> sudo systemctl stop mongod

###########################
#####  [7] MongoDB  #######
###########################

def dump_to_mongodb(messages_list: Any, config_file: str = "mongodb.conf"):
    """
    Dump all messages (one by one) converted to dict to a MongoDB database
    (server with mongod required).
    
    Parameters
    ----------
    messages_list : CategoryXX object (XX = category)
        ASTERIX decoded messages list object. Its content depends on the category.
    config_file : str (optional)
        File with configuration MongoDB configuration settings. Default = "mongodb.conf"
        
    """
    try:
        with open(config_file, 'r') as file1:
            #lines = file1.readlines()
            lines = [line.rstrip('\n') for line in file1.readlines()]
            
        # Connect to MongoDB database (it is compulsory to have one mongod server)
        client = MongoClient(lines[0])
        db = client[lines[1]]
        coleccion = db[lines[2]]
           
        data_dict = {}
        #data_dict_aux= {}
        i, j = 0, 0
        
        for i in range(messages_list.count):
            for j in range(len(messages_list.messages[i].blocks)):
                message = messages_list.messages[i].blocks[j]
                attribute_items = list(message.__dict__.keys())
                
                for item in attribute_items[1:]:
                    value = getattr(message, item)
                    #print("Valor actual:", valor_actual)
                    if value.exist: 
                        #data_dict_aux[item] = asdict(value)  
                        data_dict[item] = asdict(value)
                    else:
                        data_dict[item] = None
                #data_dict[str(i)] = data_dict_aux
                #data_dict_aux = {}
                
                coleccion.insert_one(data_dict)
                data_dict = {}
        #db.dropDatabase()
        client.close()
        
        print(f"Dumped data to MongoDB database: {lines[1]}\n")
        
    except Exception as e:
        print(f"Error dumping into MongoDB: {e}\n")
      
        
              
##############################################################################       
# Dump to database (SQLite)       
        
###########################
##### [8] SQLite DB #######
###########################

def dump_to_sqlite(filename: str, messages_list: Any):
    """
    Dump all messages (one by one) converted to dict to a SQlite database
    
    Parameters
    ----------
    filename : str 
        Database name to dump ASTERIX messages.
    messages_list : CategoryXX object (XX = category)
        ASTERIX decoded messages list object. Its content depends on the category.
        
    """
    try:
        # Create/connect to SQLite database
        conexion = sqlite3.connect(filename)
        
        # Create table
        cursor = conexion.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dictionary_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT
            )
        ''')
        
        data_dict = {}
        i, j = 0, 0
        
        for i in range(messages_list.count):
            for j in range(len(messages_list.messages[i].blocks)):
                message = messages_list.messages[i].blocks[j]  
                data_dict = asdict(message)
                
                # Convert dict to json
                data = json.dumps(data_dict)
                
                # Insert json into database
                cursor.execute('INSERT INTO dictionary_data (data) VALUES (?)', (data,))
        
                data_dict = {}
        
        # Save and close connection
        conexion.commit()
        conexion.close()  
        
        print(f"Dumped data to SQLite database: {filename}\n")
        
    except Exception as e:
        print(f"Error dumping into SQLite database: {e}\n")    
        
        
                
##############################################################################       
# Save one message (all its blocks) into human format on a variable      
        
###################################
##### [9] Message to string #######
###################################

def message_str(message: Any):
    """
    Save one message data into human format on a variable.
    
    Parameters
    ----------
    message : str
        AsterixMessage decoded object. 
        
    """
    try:
        str_info = ('********************************************\n'
                    '*******   Decoded ASTERIX Message:   *******\n'
                    '********************************************\n\n'
                    f'{message.info}\n' 
                    '********************************************\n\n')
        #for block in message.blocks:
        for index, block in enumerate(message.blocks): 
            str_info += f'  Block {index}:\n--------------\n\n'
            attribute_items = list(block.__dict__.keys())
            # Iterar sobre los atributos en el orden de declaración
            for item in attribute_items[1:]:
                value = getattr(block, item)
                #print("Valor actual:", valor_actual)
                if value.exist: 
                    str_info += str(value) + "\n"
                else:
                    str_info += f'{item.capitalize()}: None\n\n'
            str_info += "\n--------------------------------------------\n"
            
        return str_info
    
        print("Message saved correctly\n")
        
    except Exception as e:
        print(f"Error saving message: {e}\n")    



##############################################################################       
# Dump choosen items of message into txt file (CAT21)

######################################
#####  [10] CAT21 Items to TXT  ######
######################################
 
def dump_items_txt(filename: str, messages_list: Any, items_to_save: []):
    """
    Dump choosen items of messages into txt file (designed for category 21)
    
    Parameters
    ----------
    filename : str 
        Name of file to dump decoded messages.
    messages_list : CategoryXX object (XX = category)
        ASTERIX decoded messages list object. Its content depends on the category.
    items_to_save : list
        List with names of items to save
        
    """
    try:
        data_dict = {}
        values = []
        i, j = 0, 0
        with open(filename, "w") as file1:
            #for item in items_to_save:
            #    file1.write(item + "   ")
            #file1.write("\n")
            
            message = messages_list.messages[i].blocks[j]
            data = ({attr: getattr(message, attr) for 
                    attr in items_to_save})

            header = ""
            header_keys = []
            for key, value in data.items():
                dictionary = asdict(value)
                header_keys += list(dictionary.keys())
            header = '\t'.join(header_keys)
            file1.write(header + "\n")
            
            for i in range(len(messages_list.messages)):
                for j in range(len(messages_list.messages[i].blocks)):
                    message = messages_list.messages[i].blocks[j]
                    data = ({attr: getattr(message, attr) for 
                            attr in items_to_save})

                    for item in items_to_save:
                        if data[item].exist:
                            #print(asdict(datos_a_guardar[item]))
                            data_dict = asdict(data[item])
                            for value in data_dict.values():
                                values.append(str(value))
                        else:
                            data_dict = asdict(data[item])
                            for value in data_dict.values():
                                values.append(str(None))
                    values_str = '\t'.join(values)
                    file1.write(values_str + "\n")
                    
                    data_dict, values, values_str = {}, [], ""
                    
        print("Data dumped to txt!\n")

    except Exception as e:
        print(f"Error dumping to txt: {e}\n")    



##############################################################################       
# Dump choosen items of message (only hex BDS)  into txt file (CAT48)

#####################################
#####  [11] CAT48 BDS to TXT   ######
#####################################

def dump_bds_txt(filename: str, messages_list: Any):
    """
    Dump choosen items of message (only hex BDS) into txt file (designed for 
    category 48)
    
    Parameters
    ----------
    filename : str 
        Name of file to dump decoded messages.
    messages_list : CategoryXX object (XX = category)
        ASTERIX decoded messages list object. Its content depends on the category.
        
    """
    try:
        
        classmodes.bds_to_file(filename, messages_list)     
            
    except Exception as e:
        print(f"Error dumping to txt: {e}\n")  



##############################################################################
# Dump BDS category into txt file (CAT48)

###################################
#####  [12] TXT BDS Category  #####
###################################
 
def dump_bds_cat_txt(input_file: str, output_file: str, bds_type: str):
    """
    Dump BDS category (Item250) decoded into txt file (designed for category 48)
    
    Parameters
    ----------
    input_file : str
        Name of the file to read BDS hex data (generated with dump_bds_txt()).
    output_file : str
        Name of file to dump decoded messages.
    bds_type : str
        BDS type to decode
        
    """
    try:
    
       classmodes.print_in_file(input_file, output_file, bds_type)

    except Exception as e:
        print(f"Error dumping to txt: {e}\n")  



##############################################################################
# Merge on csv file CAT21 items with BDS50 and BDS60 decoded data, given a 
# max. deviation based on time (s)

####################################################
#####  [13] Merge items CAT21 and BDS50 BDS60  #####
####################################################

def merge_data(fileCAT21: str, fileBDS50: str, fileBDS60: str, output_file: str, max_dev: float = 5):
    """
    Merge on csv file CAT21 items with BDS50 and BDS60 decoded data, given a 
    max. deviation based on time (s). It is recommended to set max. deviation
    to values > 3s to obtain better results (Recommended: 5 seconds). More than 
    30 seconds can lead to erroneous data.
    
    Parameters
    ----------
    fileCAT21 : str
        Name of file with CAT21 items (generated with dump_items_txt()).
    fileBDS50 : str
        Name of file with BDS50 items (generated with dump_bds_cat_txt()).
    fileBDS60 : str
        Name of file with BDS50 items (generated with dump_bds_cat_txt()).
    max_dev : float (optional)
        Max. deviation to merge data depending on timestamp of data (5s recommended)
        
    """
    try:
    
       meteotool.merge_data(fileCAT21, fileBDS50, fileBDS60, output_file, max_dev)

    except Exception as e:
        print(f"Error merging data: {e}")  



###############################################################################
# Calculate dataframe with ASTERIX and ERA5 meteo data (temperature and 
# wind velocity)

########################################
#####  [14] Calculate meteo index  #####
########################################

def calculate_meteo(input_file: str, output_file: str, local_meteo_grid: str):
    """
    Calculate dataframe with ASTERIX and ERA5 meteo data (temperature and 
    wind velocity). It creates a dataframe with temperature and wind velocity 
    calculated with de CAT21 and BDS data, merged with the same ERA5 data obtained
    with "fastmeteo package" querying to official page 
    (https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview)
    (https://pypi.org/project/fastmeteo/)
    
    Parameters
    ----------
    input_file : str
        Name of file with all meteo data (generated with merge_data()).
    output_file : str
        Name of file to save data.
    local_meteo_grid : str
        Local grid to store ERA5 data (Note: Be careful, it uses a lot of space,
                                       Example: 5GB for Spain 24h data)
        
    """
    try:
    
       meteotool.calculate_meteo(input_file, output_file, local_meteo_grid)

    except Exception as e:
        print(f"Error calculating meteo data: {e}")  


