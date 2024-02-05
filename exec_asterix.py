#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 19:49:31 2024

@author: rodrigo
"""

import pandas as pd
import jsonpickle
import pickle
import csv
import json
from pymongo import MongoClient
from dataclasses import dataclass, asdict, fields
from typing import List, Any, Dict
import sqlite3
import logging
from typing import IO
import datetime
from tqdm import tqdm
import codecs
import subprocess
import os

import pyasterix


#%%
#%%

##############################################################################
# Set error log configuration 

################################
###  [0] Log configuration  ####
################################

import pyasterix

pyasterix.set_log()



#%%
#%% Save data on file (same name as origin with "_HEX.txt" at the end) if "save_file"
#   is true

#################################
### [1] .ast Data extraction ####
#################################

import pyasterix

sample_filename = '/home/rodrigo/Descargas/URJC/URJC_23_24/TFG_Aero/ficheros_ast/191220-cen-000001_PAR1_ADSB.ast'
#sample_filename = '/home/rodrigo/Descargas/URJC/URJC_23_24/TFG_Aero/ficheros_ast/191220-cen-000001_PAR1_MODO_S.ast'
#sample_filename = '/home/rodrigo/Descargas/URJC/URJC_23_24/TFG_Aero/ficheros_ast/191220-cen-120001_PAR1_ADSB.ast'
message_list = []
save_file = True

pyasterix.ast_to_hex(sample_filename, message_list, save_file)


#%% Split huge files into equal lines number files
#

import pyasterix

input_file = '/home/rodrigo/Descargas/URJC/URJC_23_24/TFG_Aero/ficheros_ast/191220-cen-000001_PAR1_ADSB_HEX.txt'
#input_file = '/home/rodrigo/Descargas/URJC/URJC_23_24/TFG_Aero/ficheros_ast/191220-cen-000001_PAR1_MODO_S_HEX.txt'
#input_file = '/home/rodrigo/Descargas/URJC/URJC_23_24/TFG_Aero/ficheros_ast/191220-cen-120001_PAR1_ADSB_HEX.txt'
number_lines = 250000  
path = 'test/'
#prefix = 'ADSB_HEX_part'
prefix = 'MODE_S_HEX_part'

pyasterix.split_file(input_file, prefix, number_lines, path)



#%%
#%% CAT21 Test 1 -->> only for ONE message

#####################################
###  [2] Decode ASTERIX message  ####
#####################################

import pyasterix as ast


line = "150063F71B7B6BD3A70414D70101000D95011CFAA6FDAE330E7D5334FED7199A3421083840AF3840BF08C40FF315A0120336020A40020A063F2E683840EA242173C75E2000C3200818D001F7C35940070517070303050703031C170907C40858000000"

message_asterix21 = ast.decode_message(line)


#%%
#%% CAT21 and CAT48 Test, decoded into variable

###############################################
###  [3.1] Decode ASTERIX messages (file)  ####
###############################################

import pyasterix

#file1 = "ADSB_HEX.txt"
#file1 = "test/ADSB_HEX_part_00.txt"
#file1 = "test/MODE_S_HEX_part_00.txt"
#file1 = "MODE_S_HEX.txt"
file1 = '/home/rodrigo/Descargas/URJC/URJC_23_24/TFG_Aero/ficheros_ast/191220-cen-000001_PAR1_ADSB_HEX.txt' #CAT21
#file1 = '/home/rodrigo/Descargas/URJC/URJC_23_24/TFG_Aero/ficheros_ast/191220-cen-120001_PAR1_ADSB_HEX.txt' #CAT21
#file1 = "/home/rodrigo/Descargas/URJC/URJC_23_24/TFG_Aero/python_scripts/test/MODE_S_HEX_part_00.txt"
#file1 = '/home/rodrigo/Descargas/URJC/URJC_23_24/TFG_Aero/ficheros_ast/191220-cen-000001_PAR1_MODO_S_HEX.txt' #CAT48
cat = 21
#cat = 48
#file1 = "ADSB_HEX_big.txt"
#file1 = "/home/rodrigo/Descargas/URJC/URJC_23_24/TFG_Aero/test_cat21_little.txt"


messages_asterix = pyasterix.decode_file(file1, cat)


#%%
'''
print()
print("***************************************")
print("*******   IMPRIMIENDO MENSAJE   *******")
print("***************************************")
print()
'''

#%% Comprobar que se ha leido la longitud de todo el mensaje 
i = 1
err = 0
err_list = []
for message in messages_asterix.messages:
    
    if message.count == message.leng:
        print("{} - TRUe: |{}|-|{}|".format(i, message.count, message.leng))
    else:
        print("{} - FALSE: |{}|-|{}|".format(i, message.count, message.leng))
        err_list.append(i)
        err += 1
    i += 1
    
print("Mensajes erroneos: |{}|".format(err))




#%% From file directly decoded to json

##############################################################
###  [3.2] Decode ASTERIX messages list file to json file  ###
##############################################################

import pyasterix

input_file = "ADSB_HEX.txt"
#input_file = "MODE_S_HEX.txt"
#input_file = '/home/rodrigo/Descargas/URJC/URJC_23_24/TFG_Aero/ficheros_ast/191220-cen-000001_PAR1_ADSB_HEX.txt' #CAT21
#input_file = '/home/rodrigo/Descargas/URJC/URJC_23_24/TFG_Aero/ficheros_ast/191220-cen-000001_PAR1_MODO_S_HEX.txt' #CAT48
output_file = 'test/mensaje_asterix_asdict_pyASTERIX_21_3.json'
#output_file = 'test/mensaje_asterix_asdict_pyASTERIX_48.json'

pyasterix.decode_file_to_json (input_file, output_file)




#%% From file directly decoded to csv

###############################################################
###  [3.3] Decode ASTERIX messages list (file) to csv file  ###
###############################################################

import pyasterix

#input_file = "ADSB_HEX.txt"
input_file = "test/MODE_S_HEX_part_00.txt"
output_file = "test/ejemplo_2.csv"

pyasterix.decode_file_to_csv(input_file, output_file)




#%% From variable to csv

############################################################
###  [3.4] Dump ASTERIX messages list (var) to csv file  ###
############################################################

import pyasterix

csv_file = "test/ASTERIX_cat21.csv"

pyasterix.var_to_csv(csv_file, messages_asterix)




#%%
#%% Dump object messages (transformed to dict) to JSON file 

##################################
#####  [4] Dump all to JSON  #####
##################################

import pyasterix


file1 = 'test/mensaje_asterix_asdict_pyASTERIX_21_+++.json'
#file1 = 'test/mensaje_asterix_asdict_pyASTERIX_48_4.json'

pyasterix.dump_all_to_json(file1, messages_asterix)
#pyasterix.dump_all_to_json_bk(file1, messages_asterix)




#%%
#%%

########################################
###  [5] Dump and load JSONPICKLE  ####
########################################

import pyasterix

file1 = 'test/mensaje_asterix_pyASTERIX_pickle.json'

pyasterix.dump_to_jsonpickle(file1, messages_asterix)


#%% Load object


import pyasterix

file1 = 'test/mensaje_asterix_pyASTERIX_pickle.json'

messages_asterix_2 = pyasterix.load_from_jsonpickle(file1)



#%%
#%% Dump to CSV from JSON (JSON from [4])
# Note 1: check [3.3] for file-csv conversion
# Note 2: check [3.4] for var-csv conversion

#######################
#####   [6] CSV   #####
#######################


import pyasterix

json_filename = "test/mensaje_asterix_asdict_pyASTERIX_21_+++.json"
csv_filename = "test/ejemplo_1.csv"

pyasterix.dump_to_csv(json_filename, csv_filename)



#%%
#%% Dump to MongoDB

##########################
#####  [7] MongoDB  ######
##########################


import pyasterix
 
pyasterix.dump_to_mongodb(messages_asterix)




#%%
#%% Dump to SQLite database 

###########################
##### [8] SQLite DB #######
###########################

import pyasterix

file1 = "test/mensaje_asterix_asdict_pyASTERIX_48.db"

pyasterix.dump_to_sqlite(file1, messages_asterix)



#%%
#%%Save one message (all its blocks) into human format on a variable  
   
        
###################################
##### [9] Message to string #######
###################################

import pyasterix

info_message = pyasterix.message_str(messages_asterix.messages[0])

print(info_message)



#%%
#%% Dump choosen items of message into txt file (CAT21)

######################################
#####  [10] CAT21 Items to TXT  ######
######################################

import pyasterix
from dataclasses import dataclass, asdict, fields


file1 = 'test/mi_archivo_cat21.txt'

items_to_save = ["item080", "item131", "item140", "item073",
                 "item170", "item020"]  

pyasterix.dump_items_txt(file1, messages_asterix, items_to_save)
    

#%%

import pandas as pd

fichero1 = "test/mi_archivo_cat21.txt"
datos3 = pd.read_csv(fichero1, delimiter='\t', engine='python')


#%%
#%%  Dump choosen items of message (only hex BDS)  into txt file (CAT48)

#####################################
#####  [11] CAT48 BDS to TXT  ######
#####################################
 
import pyasterix

file1 = "test/mi_archivo_cat48.txt"

pyasterix.dump_bds_txt(file1, messages_asterix)

#%%

import pandas as pd

fichero1 = "test/mi_archivo_cat48.txt"
datos3 = pd.read_csv(fichero1, delimiter='\t', engine='python')


#%%

print(messages_asterix.messages[17].blocks[0].item240.exist)


#%%
#%% Dump BDS category into txt file (CAT48)

###################################
#####  [12] TXT BDS Category  #####
###################################
 

import pyasterix

input_file = "test/mi_archivo_cat48.txt"
output_file = "test/mi_archivo_cat48_BDS50.txt"
#output_file = "test/mi_archivo_cat48_BDS50_2.txt"
#output_file = "test/mi_archivo_cat48_pyASTERIX_BDS60.txt"
bds_type = "BDS50"

pyasterix.dump_bds_cat_txt(input_file, output_file, bds_type)


#%%

import pandas as pd

fichero1 = "test/mi_archivo_cat48_BDS50.txt"
datos3 = pd.read_csv(fichero1, delimiter='\t', engine='python')


#%%
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#%% Extra: mirar si da tiempo


import pandas as pd

def unir_datos(fichero1, fichero2, columna1, columna2, desviacion_maxima=0.1):
    # Leer datos de ambos ficheros
    datos1 = pd.read_csv(fichero1, delimiter='   ') #parse_dates=[columna1])
    datos2 = pd.read_csv(fichero2, delimiter='   ') #parse_dates=[columna2])

    # Fusionar datos basándonos en la columna de hora con una desviación máxima
    #datos_fusionados = pd.merge_asof(datos1, datos2, on='hora', direction='nearest', tolerance=pd.Timedelta(desviacion_maxima, unit='s'))
    datos_fusionados = pd.merge_asof(
        datos1, datos2,
        left_on=columna1, right_on=columna2,
        direction='nearest', tolerance=pd.Timedelta(desviacion_maxima, unit='s')
    )


    return datos_fusionados

# Ejemplo de uso
fichero1 = "test/mi_archivo_cat21.txt"
fichero2 = "test/mi_archivo_cat48.txt"
columna1 = 'time_rec_pos'
columna2 = 'Time'

datos_unidos = unir_datos(fichero1, fichero2, columna1, columna2)

# Imprimir los datos fusionados
print(datos_unidos)

#%%  
#%%   IMPORTANTE -->> LAS PRUEBAS BUENAS ESTAN AQUI


import pandas as pd

# Ejemplo de uso
fichero1 = "test/mi_archivo_cat21.txt"
#fichero2 = "test/mi_archivo_cat48.txt"
fichero2 = "test/mi_archivo_cat48_BDS50.txt"
columna1 = 'time_rec_pos'
#columna2 = 'Time'
columna2 = 'Timestamp'
desviacion_maxima = 10

datos1 = pd.read_csv(fichero1, delimiter='\t', engine='python') # parse_dates=[columna1])
datos2 = pd.read_csv(fichero2, delimiter='\t', engine='python') # parse_dates=[columna2])

# Drop all rows with Nan merge column
datos1 = datos1.dropna(subset=[columna1])
datos2 = datos2.dropna(subset=[columna2])

# Sort de df by merge column
datos1 = datos1.sort_values(columna1)
datos2 = datos2.sort_values(columna2)

#%%

# Fusionar basándote en la columna numérica con una tolerancia de +-0.5

merged_data = pd.merge_asof(
    datos1, datos2,
    left_on=columna1, right_on=columna2,
    direction='nearest', tolerance=desviacion_maxima
)


#%% Para BDS44, porque no encuentra ninguna coincoincidencia

merged_data = merged_data.dropna(subset=['Timestamp'])

valor_deseado = '3424C2'
nuevo_df = merged_data[merged_data['target_addr'] == valor_deseado]


#%%

merged_data_2 = merged_data[merged_data['target_addr'] == merged_data['ICAO']]




#%%

# Escribir el DataFrame en un archivo de texto (txt)
ruta_del_archivo = "test/merges/mi_archivo_cat48_BDS50_merge.txt"
merged_data_2.to_csv(ruta_del_archivo, sep='\t', index=False)






#%%
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#%%Extra: validaciones que usaba durante el proceso de desarrollo







#%%
#%%
#%% CAT48 Test

##############################
#####       CAT48       ######
##############################




#%%
#%% ModeS Test (CAT48 Asterix - BDS)

import classmodes 
import pyModeS as pms


bds_message = "BC95E4B0A80000"

bdsdata1 = classmodes.ModeS()

bdsdata1.detect_BDS(bds_message)



bdsdata2 = pms.bds.infer("A0001692" + bds_message + "8BD87B") 



#%% -- TEST 1 --- : Comparación infer pyModesS y classModeS (con tipo BDS del item 250)


import classmodes 
import pyModeS as pms

mess_correct, mess_err, no_valid = 0, 0, 0
data_dict = {}
i, j = 0, 0
no_valid_bds = ["BDS10", "BDS17", "BDS20", "BDS30", "BDS40", "BDS45"]
#mensaje = messages_asterix21.messages[7].blocks[0]

for i in range(messages_asterix.count):
    #print("LONGITUD LISTA: {}".format(len(messages_asterix21.messages[i].blocks)))
    for j in range(len(messages_asterix.messages[i].blocks)):
        
        mensaje = messages_asterix.messages[i].blocks[j]
        
        nombre_atributo = "item250"
        # Iterar sobre los atributos en el orden de declaración
        
        valor_actual = getattr(mensaje, nombre_atributo)
        #print("Valor actual:", valor_actual)
        if valor_actual.exist: 
            for bds in valor_actual.blocks:
                
                #Con classModeS
                bdsdata1 = ""
                bdsdata1 = ','.join(bds.bdsdata.bds_type)
                #print("** {} **".format(bds.bdsdata.bds_type[0]))
                
                #Con pyModeS 
                bds_message = bds.bdsdatahex
                bdsdata2 = pms.bds.infer("A0000000" + bds_message + "000000")
                if not (bdsdata2 is None):
                    bdsdata2_list = bdsdata2.split(',')
                #print("-- {} --".format(bdsdata2))
                
                if bdsdata1 == bdsdata2:
                    #print("{} == {}".format(bdsdata1, bdsdata2))
                    mess_correct += 1
                elif not (bdsdata2 is None) and any(elemento in no_valid_bds for elemento in bdsdata2_list):
                    #print("{} ^ {}".format(bdsdata1, bdsdata2))
                    no_valid += 1
                else:
                    print("Error: {} != {}".format(bdsdata1, bdsdata2))
                    mess_err += 1
                    
                    
print("Aciertos: |{}|".format(mess_correct))
print("Errores: |{}|".format(mess_err))
print("No valido: |{}|".format(no_valid))
                #data_dict[nombre] = asdict(valor_actual)


#bds_type = pms.bds.bds60.is60(msg)



#%%   -- ?¿ --

import pyModeS as pms


msg1 = "BC95E4B0A80000"

bds_dict = {}
bdsdata = messages_asterix.messages[0].blocks[0].item250
print(bdsdata)

for i in range(4000):
    bdsdata = messages_asterix.messages[i].blocks[0].item250
    for bdsblock in bdsdata.blocks:
        print(bdsblock.bdsdata)
        try:
            bds_dict[bdsblock.bdsdata] = pms.bds.infer("A0001692" + bdsblock.bdsdatahex + "8BD87B")

        except IndexError as e:
                print(f"Error: {e}|{i}")
            

print("-----------------------------------------")

for clave, valor in bds_dict.items():
    if valor == "BDS50":
        print(f'Clave: {clave}, Valor: {valor}')


    
#%%        
#%%

print(messages_asterix.messages[0].blocks[0].item250)


#%% ADS-B Aircraft identification mapping decoder y DataItem I021/170

char_mapping = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ#####_###############0123456789######"
ads_b = "001011001100001101110001110000110010110011100000"
aircraft_id = ""

char_len = 6
count_bits = 0
i = 0
while i < 8:
    aux_char = ads_b[count_bits:count_bits+char_len]
    print("Bits: {}".format(aux_char))
    aux_map = int(aux_char,2)
    
    #print(chr(aux_map))
    
    aircraft_id += char_mapping[aux_map]
    #print(char_mapping[aux_map])
    count_bits += char_len
    i += 1  

print("Aircraft ID: {}".format(aircraft_id))




    
#%% 
#%% --- TEST BDS y pyModeS ---


import pyModeS as pms


#bds_message = "80192D334004EF"
#bds_message = "F9363D3BBF9CE9" #BDS50
#bds_message = "A74A072BFDEFC1" #BDS60
#bds_message = "185BD5CF400000" #BDS44

bds_message = "19529D00400000" #BDS44

flagg = pms.bds.bds44.is44("A0001692" + bds_message + "8BD87B")

pms.commb.wind44()
bds_pms = pms.bds.infer("A0001692" + bds_message + "8BD87B", mrar=True)
bds_pms_1 = pms.bds.infer("A0001692185BD5CF400000DFC696")
bds_pms_2 = pms.bds.infer("A80004AAA74A072BFDEFC1D5CB4F") 
#%%

#msg = "A0001692" + bds_message + "8BD87B"
msg = "A80006AC" + bds_message + "8F1E1D"

roll = pms.commb.roll50(msg) 
trk50 = pms.commb.trk50(msg)
rtrk50 = pms.commb.rtrk50(msg)
gs50 = pms.commb.gs50(msg)
tas50 = pms.commb.tas50(msg)

hdg60 = pms.commb.hdg60(msg) # 110.391, heading (deg)
ias60 = pms.commb.ias60(msg) # 259, ISA (kt)
mach60 = pms.commb.mach60(msg) # 0.7, Mach (-)
vr60baro = pms.commb.vr60baro(msg) # -2144, baro vertical rate (ft/min)
vr60ins = pms.commb.vr60ins(msg) 
    


#%% --- TEST 2 ---

import classmodes

#bds_message = "F9363D3BBF9CE9" #BDS50
#bds_message = "A74A072BFDEFC1" #BDS60
#bds_message = "185BD5CF400000" #BDS44
bds_message = "E519F331602401" #BDS50 o BDS60 - Type1
#bds_message = "FFFB23286004A7" #BDS50 o BDS60 - Type2
altitude = 38000

bdsdata = classmodes.ModeS()

bdsdata.detect_BDS(bds_message, altitude)

print(bdsdata)
    
#%%

bds_message = "F9363D3BBF9CE9" #BDS50
bds_pms = pms.bds.infer("A0001692" + bds_message + "8BD87B")

print(pms.icao("A0001692" + bds_message + "8BD87B") )



