# AsterixParse

[eurocontrol]: https://www.eurocontrol.int/asterix

Python package for decoding ASTERIX (All-Purpose Structured EUROCONTROL Surveillance Information Exchange) data protocol.  
Currently compatible with:
   - Category 21 - ADS-B Target Reports
   - Category 48 - Monoradar Target Reports
    
Also includes a decoder for Item250 (Mode-S BDS Data) of both categories, containing the following message types:
   - BDS44 - Meteorological routine air report
   - BDS50 - Track and turn report
   - BDS60 - Heading and speed report
    
All specifications and category details can be found on the official [EUROCONTROL][eurocontrol] website.
    
Compatible with Linux, Windows and MacOS envs. Recommended for use in virtual environment (e.g. conda, virtualenv) or Anaconda Navigator.  
Package created with Spyder IDE 5.4.3 and Python 3.11. 

Package developed by Rodrigo Perela Posada, student at EIF, Universidad Rey Juan Carlos (URJC); with collaboration of Marius Alexandru Marinescu Belenkov, professor at EIF, URJC. Developed within the framework of the Final Degree Project of Aerospace Engineering in Aeronautics.


## Installation

To install package on virtual env:

```pip install -i https://test.pypi.org/simple/ asterixparse```

(temporary)


## Import


```import asterixparse as ast```

> **_NOTE:_** On first import, a logging file is created on directory (`errors.log`). It will contain all the messages whose decoding has been erroneous.


## Usage


To see all the detailed functionality of the package, check the file `exec_asterix.py`. 
It includes examples of use and brief function descriptions.

#### List of funcionalities:


#### Convert binary `.ast` file to `hex` file

```bash
ast.ast_to_hex(input_file, message_list, save_file)     # Convert .ast data to hexadecimal
ast.split_file(input_file, prefix, number_lines, path)  # Split huge files into equal lines number files
```

#### Decode ASTERIX messages 

```bash
ast.decode_message(hex_message)                     # Decode one hex ASTERIX message   
ast.decode_file(input_file, category)               # Decode hex file into variable
ast.decode_file_to_json (input_file, output_file)   # Decode from hex file to JSON
ast.decode_file_to_csv(input_file, output_file)     # Decode from hex file to csv
```
> **_NOTE:_** Only decodes messages on hexadecimal, one by line files

#### Error log configuration

```bash
ast.set_log()       # Set error log configuration 
```

#### Dump decoded messages to file 

```bash
ast.var_to_csv(csv_file, messages_asterix)              # Dump ASTERIX messages list (var) to csv file
ast.dump_all_to_json(output_file, decoded_messages)     # Dump ASTERIX messages list (var) to JSON file 
ast.dump_to_jsonpickle(output_file, decoded_messages)   # Dump messages list (var type object) to json file 
ast.load_from_jsonpickle(input_file)                    # Load messages list (var type object) from json file
ast.dump_to_csv(json_filename, csv_filename)            # Dump to csv from JSON file (generated with ast.dump_all_to_json())
ast.dump_to_mongodb(decoded_messages)                   # Dump to MongoDB (requires MongoDB server)
ast.dump_to_sqlite(output_file, decoded_messages)       # Dump to SQLite database 
```

#### Experimental: 

```bash
ast.message_str(decoded_message)                                      # Save one message into human format on a variable  
ast.dump_items_txt(output_file, decoded_messages, items_to_save)      # Dump choosen items of message into txt file (CAT21)
ast.dump_bds_txt(output_file, decoded_messages)                       # Dump choosen items of message (only hex BDS) into txt file (CAT48)
ast.dump_bds_cat_txt(input_file, output_file, bds_type)               # Dump BDS category decoded data into txt file (from txt gen. w/ ast.dump_bds_txt())
ast.merge_data(fileCAT21, fileBDS50, fileBDS60, output_file, max_dev) # Merge on csv file CAT21 items with BDS50 and BDS60 decoded data
ast.calculate_meteo(input_file, output_file, local_meteo_grid)        # Calculate dataframe with ASTERIX and ERA5 meteo data
```
> **_NOTE:_** This are experimental functions and its behavior may change in future. Useful for further study of certain message data.




