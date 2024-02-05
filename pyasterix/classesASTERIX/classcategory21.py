#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 15:48:46 2023

@author: rodrigo
"""

import inspect
import math
import json

from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List


######################################################

def hexabin(num = int, base = int):
  return bin(int(num, base))[2:].zfill(len(num) * int(math.log2(base)))

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val     


######################################################
@dataclass
class Item008:
    ra: int
    tc: int
    ts: int
    arv: int
    cdti_a: int
    tcas: int
    sa: int    
    
    def __init__(self):
        self.exist  = False
        self.len    = 1
        self.hex    = 0
        self.ra     = 0
        self.tc     = 0
        self.ts     = 0
        self.arv    = 0
        self.cdti_a = 0
        self.tcas   = 0
        self.sa     = 0
    
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.ra     = res[:1]
        self.tc     = int(res[1:3], 2)
        self.ts     = res[3:4]
        self.arv    = res[4:5]
        self.cdti_a = res[5:6]
        self.tcas   = res[6:7]
        self.sa     = res[7:]
        
    def __str__(self):
        return (
            f'Item008: Aircraft Operational Status\n' 
            f' TCAS Resolution Advisory active (RA): {self.ra}\n' 
            f' Target Trajectory Change Report Cap. (TC): {self.tc}\n'
            f' Target State Report Cap. (TS): {self.ts}\n'
            f' Air-Referenced Velocity Report Cap. (ARV): {self.arv}\n'
            f' Cockpit Display of Traffic Info. airbone (CDTI/A): {self.cdti_a}\n'
            f' TCAS System Status (not TCAS): {self.tcas}\n'
            f' Single Antenna (SA): {self.sa}\n')
        
        
######################################################
@dataclass
class Item010:
    sac: int
    sic: int
    
    def __init__(self):
        self.exist = False
        self.len   = 2
        self.hex   = 0
        self.sac   = 0
        self.sic   = 0
        
    def add_info(self, info):
        self.hex = info
        self.sac = int(info[:2], 16)
        self.sic = int(info[2:], 16)
        if not 0 <= self.sac <= 255 or not 0 <= self.sic <= 255:
            raise ValueError("El valor debe estar en el rango 0, 255")
        
    def __str__(self):
        return (
            f'Item010: Data Source Identification\n SAC: {self.sac}\n'
            f' SIC: {self.sic}\n')
        
    
######################################################        
@dataclass        
class Item015:
    service_id: int
    
    def __init__(self):
        self.exist      = False
        self.len        = 1
        self.hex        = 0
        self.service_id = 0

    def add_info(self, info):
        self.hex = info
        self.service_id = hexabin(info, 16)
        
    def __str__(self):
        return (
            f'Item015: Service Identification\n'
            f' Service Identification: {self.service_id}\n')


######################################################        
@dataclass        
class Item016:
    rp: int
    
    def __init__(self):
        self.exist = False
        self.len   = 1
        self.hex   = 0
        self.rp    = 0
        
    def add_info(self, info):
        self.hex = info
        self.rp = int(info, 16)*0.5
        
    def __str__(self):
        return (
            f'Item016: Service Management\n'
            f' Report Period (RP): {self.rp}\n')
                
        
######################################################        
@dataclass        
class Item020:
    ecat: int
    
    def __init__(self):
        self.exist = False
        self.len   = 1
        self.hex   = 0
        self.ecat  = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.ecat = int(res, 2)
        
    def __str__(self):
        return (
            f'Item020: Emiter Category\n'
            f' Emiter Category (ECAT): {self.ecat}\n')
                

######################################################        
@dataclass
class Item040:
    primary: 'Item040.Primary()'
    first_ext: 'Item040.FirstExt()'
    second_ext: 'Item040.SecondExt()'
    third_ext: 'Item040.ThirdExt()'
    fourth_ext: 'Item040.FourthExt()'
        
    @dataclass
    class FourthExt:
        mbc: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.mbc   = 0
            self.fx    = 0   # There is no more documentacion about this FX
       
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.exist = True 
            self.mbc = res[:1]
            if self.mbc == '1':
                self.mbc = res[1:7]
            self.fx  = res[7:]
            count_octets += self.len
            return count_octets
            
        def __str__(self, item):
            if self.exist:
                return (
                    f' Maximum Bits Corrected (MBC): {self.mbc}\n')
            return ""

    @dataclass
    class ThirdExt:
        tbc: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.tbc   = 0
            self.fx    = 0
       
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.exist = True 
            self.tbc = res[:1]
            if self.tbc == '1':
                self.tbc = res[1:7]
            self.fx  = res[7:]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.fourth_ext.add_info(item, info, count_octets)
            return count_octets
            
        def __str__(self, item):
            if self.exist:
                return (
                    f' Total Bits Corrected (TBC): {self.tbc}\n' + item.fourth_ext.__str__(item))
            return ""
            
    @dataclass 
    class SecondExt:
        llc: int
        ipc: int
        nogo: int
        cpr: int
        ldpj: int
        rcf: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.spare = 0
            self.llc   = 0
            self.ipc   = 0
            self.nogo  = 0
            self.cpr   = 0
            self.ldpj  = 0
            self.rcf   = 0
            self.fx    = 0
            
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.exist = True 
            self.spare = res[:1]
            self.llc = res[1:2]
            self.ipc  = res[2:3]
            self.nogo = res[3:4]
            self.cpr = res[4:5]
            self.ldpj = res[5:6]
            self.rcf = res[6:7]
            self.fx  = res[7:]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.third_ext.add_info(item, info, count_octets)
            return count_octets
         
        def __str__(self, item):
            if self.exist:
                return (
                    f' List Lookup Check (LLC): {self.llc}\n'
                    f' Independent Position Check (IPC): {self.ipc}\n'
                    f' No-go Bit Status (NOGO): {self.nogo}\n'
                    f' Compact Position Reporting (CPR): {self.cpr}\n'
                    f' Local Decoding Position Jump (LDPJ): {self.ldpj}\n'
                    f' Range Check (RCF): {self.rcf}\n' + item.third_ext.__str__(item))
            return ""
        
    @dataclass    
    class FirstExt:
        dcr: int
        gbs: int
        sim: int
        tst: int
        saa: int
        cl: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.dcr   = 0
            self.gbs   = 0
            self.sim   = 0
            self.tst   = 0
            self.saa   = 0
            self.cl    = 0
            self.fx    = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.exist = True 
            self.dcr = res[:1]
            self.gbs = res[1:2]
            self.sim = res[2:3]
            self.tst = res[3:4]
            self.saa = res[4:5]
            self.cl  = int(res[5:7],2)
            self.fx  = res[7:]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.second_ext.add_info(item, info, count_octets)
            return count_octets
        
        def __str__(self, item):
            if self.exist:
                return (
                    f' Diferential Correction (DCR): {self.dcr}\n'
                    f' Ground Bit Setting (GBS): {self.gbs}\n'
                    f' Simulated Target (SIM): {self.sim}\n'
                    f' Test Target (TST): {self.tst}\n'
                    f' Selected Altitude Available (SAA): {self.saa}\n'
                    f' Confidence level (CL): {self.cl}\n' + item.second_ext.__str__(item))
            return ""
        
    @dataclass
    class Primary:
        atp: int
        arc: int
        rc: int
        rab: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.atp   = 0
            self.arc   = 0
            self.rc    = 0
            self.rab   = 0
            self.fx    = 0
            
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.exist = True 
            self.atp = int(res[:3],2)
            self.arc = int(res[3:5],2)
            self.rc  = res[5:6]
            self.rab = res[6:7]
            self.fx  = res[7:]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.first_ext.add_info(item, info, count_octets)
            return count_octets
        
        def __str__(self, item):
            return (
                f'Item040: Target Report Descriptor\n'
                f' Address Type (ATP): {self.atp}\n'
                f' Altitude Reporting Cap. (ARC): {self.arc}\n'
                f' Range Check (RC): {self.rc}\n'
                f' Report Type (RAB): {self.rab}\n' + item.first_ext.__str__(item))
                
            
    def __init__(self):
        self.exist      = False
        self.len        = 0
        self.hex        = 0
        self.primary    = self.Primary()
        self.first_ext  = self.FirstExt()
        self.second_ext = self.SecondExt()
        self.third_ext  = self.ThirdExt()
        self.fourth_ext = self.FourthExt()
        
    def add_info(self, info = str, count_octets = int):
        aux_count_octets = count_octets
        count_octets = self.primary.add_info(self, info, count_octets)
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets
    
    def __str__(self):
        return self.primary.__str__(self)
   

######################################################
@dataclass
class Item070:
    mode3_a: int
    
    def __init__(self):
        self.exist   = False
        self.len     = 2
        self.hex     = 0
        self.spare   = 0
        self.mode3_a = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        # Convert str bin to int, then to octal
        aux = oct(int(res[4:], 2))
        # Get rid from the initial "0o"
        self.mode3_a = aux[2:]
        
    def __str__(self):
        return (
            f'Item070: Mode 3/A in Octal Representation\n'
            f' Mode 3/A in Octal Representation: {self.mode3_a}\n')
        
    
######################################################
@dataclass
class Item071:
    time_app_pos: int
    
    def __init__(self):
        self.exist        = False
        self.len          = 3
        self.hex          = 0
        self.time_app_pos = 0
      
    def add_info(self, info):
        self.hex = info
        self.time_app_pos = int(hexabin(info, 16), 2)/128
        
    def __str__(self):
        delta = timedelta(seconds=self.time_app_pos)
        midnight = datetime(1, 1, 1, 0, 0, 0)
        date_time = midnight + delta
        
        return (
            f'Item071: Time of Applicability for Position\n'
            f' Time of Applicability for Position: {self.time_app_pos}\n'
            " Time format: {:02d}:{:02d}:{:02d},{:06d}\n".format(date_time.hour, 
              date_time.minute, date_time.second, date_time.microsecond))
    

######################################################       
@dataclass        
class Item072:
    time_app_vel: int
    
    def __init__(self):
        self.exist        = False
        self.len          = 3
        self.hex          = 0
        self.time_app_vel = 0
      
    def add_info(self, info):
        self.hex = info
        self.time_app_vel = int(hexabin(info, 16), 2)/128
    
    def __str__(self):
        delta = timedelta(seconds=self.time_app_vel)
        midnight = datetime(1, 1, 1, 0, 0, 0)
        date_time = midnight + delta

        return (
            f'Item072: Time of Applicability for Velocity\n'
            f' Time of Applicability for Velocity: {self.time_app_vel}\n'
            " Time format: {:02d}:{:02d}:{:02d},{:06d}".format(date_time.hour, 
              date_time.minute, date_time.second, date_time.microsecond))
    
    
######################################################
@dataclass
class Item073:
    time_rec_pos: int
    
    def __init__(self):
        self.exist        = False
        self.len          = 3
        self.hex          = 0
        self.time_rec_pos = 0
      
    def add_info(self, info):
        self.hex = info
        self.time_rec_pos = int(hexabin(info, 16), 2)/128
        
    def __str__(self):
        delta = timedelta(seconds=self.time_rec_pos)
        midnight = datetime(1, 1, 1, 0, 0, 0)
        date_time = midnight + delta

        return (
            'Item073: Time of Message Reception for Position\n'
            f' Time of Message Reception for Position: {self.time_rec_pos}\n'
            " Time format: {:02d}:{:02d}:{:02d},{:06d}\n".format(date_time.hour, 
              date_time.minute, date_time.second, date_time.microsecond))
    
    
######################################################
@dataclass
class Item074:
    fsi: int
    time_rec_poshf: int
    
    def __init__(self):
        self.exist          = False
        self.len            = 4
        self.hex            = 0
        self.fsi            = 0
        self.time_rec_poshf = 0
      
    def add_info(self, info):
        self.hex = info
        self.fsi = hexabin(info[:1], 16)
        self.time_rec_poshf = int(hexabin(info[1:], 16), 2)*pow(2,-30)
        
    def __str__(self):
        delta = timedelta(seconds=self.time_rec_poshf)
        midnight = datetime(1, 1, 1, 0, 0, 0)
        date_time = midnight + delta
        
        return (
            f'Item074: Time of Message Reception for Position-High Precision\n'
            f' Full Second Indicator (FSI): {self.fsi}\n'
            f' Time of Message Reception for Position-High Precision: {self.time_rec_poshf}\n'
            " Time format: {:02d}:{:02d}:{:02d},{:08d}\n".format(date_time.hour, 
              date_time.minute, date_time.second, date_time.microsecond))
    
    
######################################################
@dataclass
class Item075:
    time_rec_vel: int
    
    def __init__(self):
        self.exist        = False
        self.len          = 3
        self.hex          = 0
        self.time_rec_vel = 0
      
    def add_info(self, info):
        self.hex = info
        self.time_rec_vel = int(hexabin(info, 16), 2)/128

    def __str__(self):
        delta = timedelta(seconds=self.time_rec_vel)
        midnight = datetime(1, 1, 1, 0, 0, 0)
        date_time = midnight + delta
        
        return (
            f'Item075: Time of Message Reception for Velocity\n'
            f' Time of Message Reception for Velocity: {self.time_rec_vel}\n'
            " Time format: {:02d}:{:02d}:{:02d},{:06d}\n".format(date_time.hour, 
              date_time.minute, date_time.second, date_time.microsecond))
    
    
######################################################
@dataclass
class Item076:
    fsi: int
    time_rec_velhf: int
    
    def __init__(self):
        self.exist          = False
        self.len            = 4
        self.hex            = 0
        self.fsi            = 0
        self.time_rec_velhf = 0
      
    def add_info(self, info):
        self.hex = info
        self.fsi = hexabin(info[:1], 16)
        self.time_rec_velhf = int(hexabin(info[1:], 16), 2)*pow(2,-30)
    
    def __str__(self):
        delta = timedelta(seconds=self.time_rec_velhf)
        midnight = datetime(1, 1, 1, 0, 0, 0)
        date_time = midnight + delta
        
        return (
            f'Item076: Time of Message Reception of Velocity-High Precision\n'
            f' Full Second Indicator (FSI): {self.fsi}\n'
            f' Time of Message Reception for Velocity-High Precision: {self.time_rec_velhf}\n'
            " Time format: {:02d}:{:02d}:{:02d},{:08d}\n".format(date_time.hour, 
              date_time.minute, date_time.second, date_time.microsecond))
    
    
######################################################
@dataclass
class Item077:
    time_report_trans: int
    
    def __init__(self):
        self.exist             = False
        self.len               = 3
        self.hex               = 0
        self.time_report_trans = 0
      
    def add_info(self, info):
        self.hex = info
        self.time_report_trans = int(hexabin(info, 16), 2)/128

    def __str__(self):
        delta = timedelta(seconds=self.time_report_trans)
        midnight = datetime(1, 1, 1, 0, 0, 0)
        date_time = midnight + delta
        
        return (
            f'Item077: Time of ASTERIX Report Transmission\n'
            f' Time of ASTERIX Report Transmission: {self.time_report_trans}\n'
            " Time format: {:02d}:{:02d}:{:02d},{:06d}\n".format(date_time.hour, 
              date_time.minute, date_time.second, date_time.microsecond))
    

######################################################       
@dataclass
class Item080:
    target_addr: int
    
    def __init__(self):
        self.exist        = False
        self.len          = 3
        self.hex          = 0
        self.target_addr  = 0
      
    def add_info(self, info):
        self.hex = info
        self.target_addr = info
        
    def __str__(self):
        return (
            f'Item080: Target Address\n'
            f' Target Address: {self.target_addr}\n')   
        
######################################################
@dataclass
class Item090:
    primary: 'Item090.Primary()'
    first_ext: 'Item090.FirstExt()'
    second_ext: 'Item090.SecondExt()'
    third_ext: 'Item090.ThirdExt()'
    
    @dataclass
    class ThirdExt:
        pic: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.pic   = 0
            self.spare = 0
            self.fx    = 0  # There is no more documentacion about this FX
       
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))            
            self.exist = True 
            self.pic = int(res[:4], 2)
            self.spare = res[4:7]
            self.fx  = res[7:]
            count_octets += self.len
            return count_octets
         
        def __str__(self, item):
            if self.exist:
                return f' PIC: {self.pic}\n'
            return ""
        
    @dataclass  
    class SecondExt:
        sils: int
        sda: int
        gva: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.spare = 0
            self.sils  = 0
            self.sda   = 0
            self.gva   = 0
            self.fx    = 0
            
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.exist = True 
            self.spare = res[:2]
            self.sils = res[2:3]
            self.sda  = res[3:5]
            self.gva = res[5:7]
            self.fx  = res[7:]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.third_ext.add_info(item, info, count_octets)
            return count_octets
           
        def __str__(self, item):
            if self.exist:
                return (
                    f' SILS: {self.sils}\n'
                    f' SDA: {self.sda}\n'
                    f' GVA: {self.gva}\n' + item.third_ext.__str__(item))
            return ""
    
    @dataclass        
    class FirstExt:
        nic_baro: int
        sil: int
        nac: int
        
        def __init__(self):
            self.exist    = False
            self.len      = 1 
            self.nic_baro = 0
            self.sil      = 0
            self.nac      = 0 
            self.fx       = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))            
            self.exist = True 
            self.nic_baro = res[:1]
            self.sil = res[1:3]
            self.nac = res[3:7]
            self.fx  = res[7:]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.second_ext.add_info(item, info, count_octets)
            return count_octets
   
        def __str__(self, item):
            if self.exist:
                return (
                    f' NICbaro: {self.nic_baro}\n'
                    f' SIL: {self.sil}\n'
                    f' NACp: {self.nac}\n' + item.second_ext.__str__(item))
            return ""
    
    @dataclass
    class Primary:
        nuc_nac: int
        nuc_nic: int
        
        def __init__(self):
            self.exist   = False
            self.len     = 1 
            self.nuc_nac = 0
            self.nuc_nic = 0
            self.fx      = 0
            
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))            
            self.exist = True 
            self.nuc_nac = res[:3]
            self.nuc_nic = res[3:7]
            self.fx  = res[7:]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.first_ext.add_info(item, info, count_octets)
            return count_octets
        
        def __str__(self, item):
            return (
                f'Item090: Quality Indicators\n'
                f' NUCr or NACv: {self.nuc_nac}\n'
                f' NUCp or NIC: {self.nuc_nic}\n' + item.first_ext.__str__(item))
        
            
    def __init__(self):
        self.exist      = False
        self.len        = 0
        self.hex        = 0
        self.primary    = self.Primary()
        self.first_ext  = self.FirstExt()
        self.second_ext = self.SecondExt()
        self.third_ext  = self.ThirdExt()
    
    def add_info(self, info = str, count_octets = int):
        aux_count_octets = count_octets
        count_octets = self.primary.add_info(self, info, count_octets)
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets

    def __str__(self):
        return self.primary.__str__(self)
   

######################################################
# REVISAR si los bloques se añaden bien y si se imprimen bien (no he encontrado
# ejemplo con este item)
# Resvisar que (res = hexabin(info_item, 16)) en TID.add_info es correcto
@dataclass
class Item110:
    tis: 'Item110.TIS()'
    tid: 'Item110.RepTID()'
    
    @dataclass
    class TID:
        tca: int
        nc: int
        tcp_num: int
        altitude: int
        latitude: int
        longitude: int
        point_type: int
        td: int
        tra: int
        toa: int
        tov: int
        ttr: int
        
        def __init__(self):
            self.len        = 15
            self.tca        = 0
            self.nc         = 0
            self.tcp_num    = 0
            self.altitude   = 0
            self.latitude   = 0
            self.longitude  = 0
            self.point_type = 0
            self.td         = 0
            self.tra        = 0
            self.toa        = 0
            self.tov        = 0
            self.ttr        = 0
        
        def add_info (self, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)            
            self.exist = True 
            self.tca = res[:1]
            self.nc =res[1:2]
            self.tcp_num = res[2:8]
            self.altitude = twos_comp(int(res[8:24], 2), len(res[8:24]))*10
            self.latitude = twos_comp(int(res[24:48], 2), len(res[24:48]))*(180/pow(2,23))
            self.longitude = twos_comp(int(res[48:72], 2), len(res[48:72]))*(180/pow(2,23))
            self.point_type = int(res[72:77],2)
            self.td = res[77:79]
            self.tra = res[79:80]
            self.toa = res[80:81]
            self.tov = int(res[81:105],2)*1
            self.ttr = int(res[105:],2)*0.01
            count_octets += self.len          
            return count_octets
     
        def __str__(self):
            return (
                f' TCA: {self.tca}\n'
                f' NC: {self.nc}\n'
                f' TCP Number: {self.tcp_num}\n'
                f' Altitude: {self.altitude}\n'
                f' Latitude: {self.latitude}\n'
                f' Longitude: {self.longitude}\n'
                f' Point_type: {self.point_type}\n'
                f' TD: {self.td}\n'
                f' TRA: {self.tra}\n'
                f' TOA: {self.toa}\n'
                f' TOV: {self.tov}\n'
                f' TTR: {self.ttr}\n')
    
    @dataclass
    class RepTID:
        rep: int
        blocks: []
    
        def __init__(self):
            self.exist  = False
            self.len    = 1
            self.rep    = 0
            self.blocks = []
        
        def add_blocks(self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            self.rep = int(info_item, 16)
            count_octets += self.len
            for i in range(self.rep): 
                new_block = self.TID()
                self.blocks.append(new_block)
                count_octets = self.blocks[i].add_info(info, count_octets)
            return count_octets
        
        
        def __str__(self):
            str_tid = ""
            if self.exist:
                for i in range(self.rep):
                    str_tid +=  f' Block {i}:\n {self.blocks[i]}\n\n'
            return str_tid
                
    @dataclass   
    class TIS:
        nav: int
        nvb: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.nav   = 0
            self.nvb   = 0
            self.spare = 0 
            self.fx    = 0 # There is no more documentacion about this FX
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = int(info_item, 16)            
            self.exist = True 
            self.nav = res[:1]
            self.nvb = res[1:2]
            self.fx = res[7:]
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    f' NAV: {self.nav}\n'
                    f' NVB: {self.nvb}\n')
            return ""
   
            
    def __init__(self):
        self.exist = False
        self.len   = 0
        self.hex   = 0
        self.tis   = self.TIS()
        self.tid   = self.RepTID()
        self.spare = 0
        self.fx    = 0  #No aparece nada sobre el uso de esta extension
        
    def add_info(self, info = str, count_octets = int):
        lenght = 1
        aux_count_octets = count_octets
        info_item = info[count_octets*2:count_octets*2+lenght*2]
        res = "{0:08b}".format(int(info_item, 16))
        count_octets += lenght
        if res[:1] == '1':
            count_octets = self.tis.add_info(self, info, count_octets)
        if res[1:2] == '1':
            count_octets = self.tid.add_blocks(self, info, count_octets)
        self.fx = res[7:]
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets
            
    def __str__(self):
        return (
            f'Item110: Trajectory Intent\n{self.tis}\n{self.tid}\n')


######################################################
@dataclass    
class Item130:
    latitude: int
    longitude: int
    
    def __init__(self):
        self.exist     = False
        self.len       = 6
        self.hex       = 0
        self.latitude  = 0
        self.longitude = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.latitude  = twos_comp(int(res[:24], 2), len(res[:24]))*(180/pow(2,23)) 
        self.longitude = twos_comp(int(res[24:], 2), len(res[24:]))*(180/pow(2,23))
        
    def __str__(self):
        return (
            f'Item130: Position in WGS-84 Co-ordinates\n'
            f' Latitude: {self.latitude}\n'
            f' Longitude: {self.longitude}\n')
  
    
######################################################        
@dataclass
class Item131:
    latitude: int
    longitude: int
    
    def __init__(self):
        self.exist     = False
        self.len       = 8
        self.hex       = 0
        self.latitude  = 0
        self.longitude = 0

    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.latitude  = twos_comp(int(res[:32], 2), len(res[:32]))*(180/pow(2,30)) 
        self.longitude = twos_comp(int(res[32:], 2), len(res[32:]))*(180/pow(2,30))
        
    def __str__(self):
        return (
            f'Item131: High-Resolution Position in WGS-84 Co-ordinates\n'
            f' Latitude: {self.latitude}\n'
            f' Longitude: {self.longitude}\n')


######################################################        
@dataclass 
class Item132:
    mam: int
    
    def __init__(self):
        self.exist = False
        self.len   = 1
        self.hex   = 0
        self.mam   = 0

    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.mam  = twos_comp(int(res, 2), len(res))*1

    def __str__(self):
        return (
            f'Item132: Message Amplitude\n'
            f' Message Amplitude: {self.mam}\n')


######################################################
@dataclass
class Item140:
    geom_height: int
    
    def __init__(self):
        self.exist       = False
        self.len         = 2
        self.hex         = 0
        self.geom_height = 0

    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.geom_height = twos_comp(int(res, 2), len(res))*6.25
        
    def __str__(self):
        return (
            f'Item140: Geometric Height\n'
            f' Geometric Height: {self.geom_height}\n')


######################################################
@dataclass
class Item145:
    fl: int
    
    def __init__(self):
        self.exist = False
        self.len   = 2
        self.hex   = 0
        self.fl    = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.fl = twos_comp(int(res, 2), len(res))*(1/4)

    def __str__(self):
        return (
            f'Item145: Flight Level\n'
            f' Flight Level: {self.fl}\n')


######################################################
@dataclass
class Item146:
    sas: int
    source: int
    altitude: int
    
    def __init__(self):
        self.exist    = False
        self.len      = 2
        self.hex      = 0
        self.sas      = 0
        self.source   = 0
        self.altitude = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.sas = res[:1] 
        self.source = res[1:3]
        self.altitude = twos_comp(int(res[3:], 2), len(res[3:]))*25

    def __str__(self):
        return (
            f'Item146: Selected Altitude\n'
            f' Source Availability (SAS): {self.sas}\n'
            f' Source: {self.source}\n'
            f' Altitude: {self.altitude}\n')


######################################################
@dataclass
class Item148:
    mv: int
    ah: int
    am: int
    altitude: int
    
    def __init__(self):
        self.exist    = False
        self.len      = 2
        self.hex      = 0
        self.mv       = 0
        self.ah       = 0
        self.am       = 0
        self.altitude = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.mv = res[:1] 
        self.ah = res[1:2]
        self.am = res[2:3]
        self.altitude = twos_comp(int(res[3:], 2), len(res[3:]))*25
      
    def __str__(self):
        return (
            f'Item148: Final State Selected Altitude\n'
            f' Manage Vertical Mode (MV): {self.mv}\n'
            f' Altitude Hold Mode (AH): {self.ah}\n'
            f' Approach Mode (AM): {self.am}\n'
            f' Altitude: {self.altitude}\n')
    
    
######################################################
@dataclass
class Item150:
    im: int
    airspeed: int
    
    def __init__(self):
        self.exist     = False
        self.len       = 2
        self.hex       = 0
        self.im        = 0
        self.airspeed  = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.im = int(res[:1], 2)
        self.airspeed = int(res[1:], 2)
        if self.im == '0':
            self.airspeed = self.airspeed*pow(2,-14)
        else:
            self.airspeed = self.airspeed*0.001
        
    def __str__(self):
        return (
            f'Item150: Air Speed\n'
            f' IAS or Mach: {self.im}\n'
            f' Air Speed: {self.airspeed}\n')
        
    
######################################################
@dataclass
class Item151:
    re: int
    true_airspeed: int
    
    def __init__(self):
        self.exist         = False
        self.len           = 2
        self.hex           = 0
        self.re            = 0
        self.true_airspeed = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.re = res[:1]
        self.true_airspeed = int(res[1:], 2)

    def __str__(self):
        return (
            f'Item151: True Aispeed\n'
            f' "Range Exceeded" Indicator: {self.re}\n'
            f' True Air Speed: {self.true_airspeed}\n')
    
    
######################################################
@dataclass
class Item152:
    mag_heading: int
    
    def __init__(self):
        self.exist       = False
        self.len         = 2
        self.hex         = 0
        self.mag_heading = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.mag_heading = int(res, 2)*(360/pow(2,16))
    
    def __str__(self):
        return (
            f'Item152: Magnetic Heading\n'
            f' Magnetic Heading: {self.mag_heading}\n')
    
    
######################################################
@dataclass
class Item155:
    re: int
    bar_vert_rate: int
    
    def __init__(self):
        self.exist         = False
        self.len           = 2
        self.hex           = 0
        self.re            = 0
        self.bar_vert_rate = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.re = res[:1]
        self.bar_vert_rate = twos_comp(int(res[1:], 2), len(res[1:]))*6.25
    
    def __str__(self):
        return (
            f'Item155: Barometric Vertical Rate\n'
            f' "Range Exceeded" Indicator: {self.re}\n'
            f' Barometric Vertical Rate: {self.bar_vert_rate}\n')
    
    
######################################################
@dataclass
class Item157:
    re: int
    geo_vert_rate: int
    
    def __init__(self):
        self.exist         = False
        self.len           = 2
        self.hex           = 0
        self.re            = 0
        self.geo_vert_rate = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.re = res[:1]
        self.geo_vert_rate = twos_comp(int(res[1:], 2), len(res[1:]))*6.25

    def __str__(self):
        return (
            f'Item157: Geometric Vertical Rate\n'
            f' "Range Exceeded" Indicator: {self.re}\n'
            f' Geometric Vertical Rate: {self.geo_vert_rate}\n')
    
    
######################################################
@dataclass
class Item160:
    re: int
    ground_speed: int
    track_angle: int
    
    def __init__(self):
        self.exist        = False
        self.len          = 4
        self.hex          = 0
        self.re           = 0
        self.ground_speed = 0
        self.track_angle  = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.re = res[:1]
        self.ground_speed = int(res[1:16], 2)*0.22
        self.track_angle = int(res[16:], 2)*(360/pow(2,16))
    
    def __str__(self):
        return (
            f'Item160: Airbone Ground Vector\n'
            f' "Range Exceeded" Indicator: {self.re}\n'
            f' Ground Speed (WGS-84): {self.ground_speed}\n'
            f' Track Angle: {self.track_angle}\n')
    
    
######################################################
@dataclass
class Item161:
    track_number: int
    
    def __init__(self):
        self.exist        = False
        self.len          = 2
        self.hex          = 0
        self.spare        = 0
        self.track_number = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.track_number = int(res[4:], 2)
        
    def __str__(self):
        return (
            f'Item161: Track Number\n'
            f' Track Number: {self.track_number}\n')   
    
    
######################################################
@dataclass
class Item165:
    tar: int
    
    def __init__(self):
        self.exist = False
        self.len   = 2
        self.hex   = 0
        self.spare = 0
        self.tar   = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.tar = twos_comp(int(res[4:], 2), len(res[4:]))*(1/32)
        
    def __str__(self):
        return (
            f'Item165: Track Angle Rate\n'
            f' Track Angle Rate (TAR): {self.tar}\n')
    
    
######################################################
@dataclass
class Item170:
    target_id: int = ""
    
    def __init__(self):
        self.exist = False
        self.len   = 6
        self.hex   = 0
        self.char1 = 0
        self.char2 = 0
        self.char3 = 0
        self.char4 = 0
        self.char5 = 0
        self.char6 = 0
        self.char7 = 0
        self.char8 = 0
        self.target_id = ""
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.char1 = res[:6]
        self.char2 = res[6:12]
        self.char3 = res[12:18]
        self.char4 = res[18:24]
        self.char5 = res[24:30]
        self.char6 = res[30:36]
        self.char7 = res[36:42]
        self.char8 = res[42:]
        
        char_map = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ#####_###############0123456789######"
        char_len = 6
        count_bits = 0
        i = 0
        while i < 8:
            aux_char = res[count_bits:count_bits+char_len]
            aux_map = int(aux_char,2)
            self.target_id += char_map[aux_map]
            count_bits += char_len
            i += 1  

    def __str__(self):
        return (
            f'Item170: Target Identification\n'
            f' Target Identification: {self.target_id}\n')
    
    
######################################################
@dataclass
class Item200:
    icf: int
    lnav: int
    me: int
    ps: int
    ss: int
    
    def __init__(self):
        self.exist = False
        self.len   = 1
        self.hex   = 0
        self.icf   = 0
        self.lnav  = 0
        self.me    = 0
        self.ps    = 0
        self.ss    = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.icf = int(res[:1], 2)
        self.lnav = int(res[1:2], 2)
        self.me = int(res[2:3], 2)
        self.ps = int(res[3:6], 2)
        self.ss = int(res[6:], 2)

    def __str__(self):
        return (
            f'Item200: Target Status\n'
            f' Intent Change Flag (ICF): {self.icf}\n'
            f' LNAV Mode (LNAV): {self.lnav}\n'
            f' Military Emergency (ME): {self.me}\n'
            f' Priority Status (PS): {self.ps}\n'
            f' Surveillance Status (SS): {self.ss}\n')
    
    
######################################################
@dataclass
class Item210:
    vns: int
    vn: int
    ltt: int
    
    def __init__(self):
        self.exist = False
        self.len   = 1
        self.hex   = 0
        self.spare = 0
        self.vns   = 0
        self.vn    = 0
        self.ltt   = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.vns = int(res[1:2], 2)
        self.vn = int(res[2:5], 2)
        self.ltt = int(res[5:], 2)

    def __str__(self):
        return (
            f'Item210: MOPS Version\n'
            f' Version Not Supported (VNS): {self.vns}\n'
            f' Version Number (VN): {self.vn}\n'
            f' Link Technology Type (LTT): {self.ltt}\n')
    
######################################################
@dataclass
class Item220:
    wind_speed: 'Item220.WindSpeed()'
    wind_direction: 'Item220.WindDirection()'
    temperature: 'Item220.Temperature()'
    turbulence:'Item220.Turbulence()'
     
    @dataclass
    class Turbulence():
        turbulence: int
        
        def __init__(self):
            self.exist          = False
            self.len            = 1 
            self.turbulence     = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = int(info_item, 16)
            self.exist = True 
            self.turbulence = res
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    f' Turbulence: {self.turbulence}\n')
            return ""

    @dataclass        
    class Temperature():
        temperature: int
        
        def __init__(self):
            self.exist       = False
            self.len         = 2 
            self.temperature = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)
            self.exist = True 
            self.wind_direction = twos_comp(int(res, 2), len(res))*0.25            
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    f' Temperature: {self.temperature}\n')
            return ""
         
    @dataclass       
    class WindDirection():
        wind_direction: int
        
        def __init__(self):
            self.exist          = False
            self.len            = 2 
            self.wind_direction = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = int(info_item, 16)
            self.exist = True 
            self.wind_direction = res
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    f' Wind Direction: {self.wind_direction}\n')
            return ""
    
    @dataclass
    class WindSpeed():
        wind_speed: int
        
        def __init__(self):
            self.exist      = False
            self.len        = 2 
            self.wind_speed = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = int(info_item, 16)            
            self.exist = True 
            self.wind_speed = res
            count_octets += self.len
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    f' Wind Speed: {self.wind_speed}\n')
            return ""

            
    def __init__(self):
        self.exist          = False
        self.len            = 0
        self.hex            = 0
        self.wind_speed     = self.WindSpeed()
        self.wind_direction = self.WindDirection()
        self.temperature    = self.Temperature()
        self.turbulence     = self.Turbulence()
        self.spare          = 0 
        self.fx             = 0  # There is no more documentacion about this FX
        
        
    def add_info(self, info = str, count_octets = int):
        aux_count_octets = count_octets
        lenght = 1 
        info_item = info[count_octets*2:count_octets*2+lenght*2]
        res = "{0:08b}".format(int(info_item, 16))
        count_octets += lenght
        
        if res[:1] == '1':
            count_octets = self.wind_speed.add_info(self, info, count_octets)
        if res[1:2] == '1':
            count_octets = self.wind_direction.add_info(self, info, count_octets)
        if res[2:3] == '1':
            count_octets = self.temperature.add_info(self, info, count_octets)
        if res[3:4] == '1':
            count_octets = self.turbulence.add_info(self, info, count_octets)
        
        self.fx = res[7:]
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets
        
    def __str__(self):
        return (
            f'Item220: Met Information\n{self.wind_speed}\n{self.wind_direction}\n'
            f'{self.temperature}\n{self.turbulence}\n')


######################################################
@dataclass
class Item230:
    roll_angle: int
    
    def __init__(self):
        self.exist      = False
        self.len        = 2
        self.hex        = 0
        self.roll_angle = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.roll_angle = twos_comp(int(res, 2), len(res))*0.01
        
    def __str__(self):
        return (
            f'Item230: Roll Angle\n'
            f' Roll Angle: {self.roll_angle}\n')
            
    
######################################################
# REVISAR si los bloques se añaden bien y quitar los "self" como parametro 
# de las llamadas a self.add_info(self, info, count_octets)
@dataclass
class Item250:
    #rep: int
    blocks: []
    
    @dataclass
    class BDS:
        bdsdata: int
        bds1: int
        bds2: int
        
        def __init__(self):
            self.exist   = False
            self.len     = 8
            self.bdsdata = 0
            self.bds1    = 0
            self.bds2    = 0
        
        def add_info (self, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info, 16)
            self.exist = True
            self.bdsdata = info_item[:-2]
            self.bds1 = res[56:60]
            self.bds2 = res[60:]
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            return (
                f' BDS Reg. Data: {self.bdsdata}\n'
                f' BDS1 Reg.Address 1: {self.bds1}\n'
                f' BDS2 Reg.Address 2: {self.bds2}\n')
     
        
    def __init__(self):
        self.exist  = False
        self.len    = 0
        self.hex    = 0
        self.rep    = 0
        self.blocks = []
        
    def add_info(self, info = str, count_octets = int):
        aux_count_octets = count_octets
        lenght = 1
        info_item = info[count_octets*2:count_octets*2+lenght*2]
        self.rep = int(info_item, 16)
        count_octets += lenght 
        
        for i in range(self.rep): 
            new_block = self.BDS()
            self.blocks.append(new_block)
            count_octets = self.blocks[i].add_info(info, count_octets)
        
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets

    def __str__(self):
        str_bds = 'Item250: BDS Register Data\n'
        if self.exist:
           for i in range(self.rep):
               str_bds +=  f' Block {i}:\n {self.blocks[i]}\n\n'
        return str_bds
    
    
######################################################
@dataclass
class Item260:
    typ: int
    styp: int
    ara: int
    rac: int
    rat: int
    mte: int
    tti: int
    tid: int
    
    def __init__(self):
        self.exist = False
        self.len   = 7
        self.hex   = 0
        self.typ   = 0
        self.styp  = 0
        self.ara   = 0
        self.rac   = 0
        self.rat   = 0
        self.mte   = 0
        self.tti   = 0
        self.tid   = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.len   = res[:5]
        self.typ   = res[5:8]
        self.styp  = res[8:16]
        self.ara   = res[16:22]
        self.rac   = res[22:26]
        self.rat   = res[26:27]
        self.mte   = res[27:28]
        self.tti   = res[28:30]
        self.tid   = res[30:]
        
    def __str__(self):
        return (
            f'Item260: ACAS Resolution Advisory Report\n'
            f' Message Type (TYP): {self.typ}\n'
            f' Message Sub-type (STYP): {self.styp}\n'
            f' Active Resolution Advisories (ARA): {self.ara}\n'
            f' RA Complement Record (RAC): {self.rac}\n'
            f' RA Terminated (RAT): {self.rat}\n'
            f' Multiple Threat Encounter (MTE): {self.mte}\n'
            f' Threat Type Indicator (TTI): {self.tti}\n'
            f' Threat Identity Data (TID): {self.tid}\n')
    
    
######################################################
@dataclass
class Item271:
    primary: 'Item271.Primary()'
    first_ext: 'Item271.FirstExt()'
    
    @dataclass
    class FirstExt:
        l_w: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.l_w   = 0
            self.spare = 0
            self.fx    = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.exist = True 
            self.l_w = int(res[:4], 16)
            self.fx  = res[7:]
            count_octets += self.len
            return count_octets
   
        def __str__(self, item):
            if self.exist:
                return (
                    f' Lenght / Width of Aircraft: {self.l_w}\n')
            return ""
   
    @dataclass
    class Primary:
        poa: int
        cdti_s: int
        b2_low: int
        ras: int
        ident: int
        
        def __init__(self):
            self.exist  = False
            self.len    = 1 
            self.spare  = 0
            self.poa    = 0
            self.cdti_s = 0
            self.b2_low = 0
            self.ras    = 0
            self.ident  = 0
            self.fx     = 0
            
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))            
            self.exist = True 
            self.poa = res[2:3]
            self.cdti_s = res[3:4]
            self.b2_low = res[4:5]
            self.ras    = res[5:6]
            self.ident  = res[6:7]
            self.fx  = res[7:]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.first_ext.add_info(item, info, count_octets)
            return count_octets
        
        def __str__(self, item):
            return (
                f'Item271: Surface Capabilities and Characteristics\n'
                f' Position Offset Applied (POA): {self.poa}\n'
                f' CDTI/S: {self.cdti_s}\n'
                f' B2 low: {self.b2_low}\n'
                f' Receiving ATC Services (RAS): {self.ras}\n'
                f' IDENT-switch: {self.ident}\n' + item.first_ext.__str__(item))
           
        
    def __init__(self):
        self.exist      = False
        self.len        = 0
        self.hex        = 0
        self.primary    = self.Primary()
        self.first_ext  = self.FirstExt()
        
        
    def add_info(self, info = str, count_octets = int):
        aux_count_octets = count_octets
        self.exist = True
        count_octets = self.primary.add_info(self, info, count_octets)
        
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets

    def __str__(self):
        return self.primary.__str__(self)

    
######################################################
# REVISAR lo del parametro "item" en las llamadas a add_info
@dataclass
class DataAge:
    data: int
    
    def __init__(self):
        self.exist = False
        self.len   = 1 
        self.data  = 0
    
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = int(info_item, 16)        
        self.exist = True 
        self.data = res*0.1
        count_octets += self.len        
        return count_octets
    
    def __str__(self):
        return f'{self.data}'
        
@dataclass
class Item295:
    octet_1: 'Item295.Octet1()'
    octet_2: 'Item295.Octet2()'
    octet_3: 'Item295.Octet3()'
    octet_4: 'Item295.Octet4()'
    
    @dataclass
    class Octet4:
        ara: DataAge()
        scc: DataAge()
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.octet = 0
            self.ara   = DataAge()
            self.scc   = DataAge()
            self.spare = 0
            self.fx    = 0
        
        def add_info (self, item, info = str, count_octets = int):
            if self.octet[0] == '1':
                count_octets = self.ara.add_info(self, info, count_octets)
            if self.octet[1] == '1':
                count_octets = self.scc.add_info(self, info, count_octets)
            if self.octet[7]:
                self.fx = self.octet[7]
            
            return count_octets
        
        def __str__(self, item):
            if self.exist:
                return f' ARA: {self.ara}\n SCC: {self.scc}\n'
            return "" 
        
    @dataclass        
    class Octet3:
        gvr: DataAge()
        gv: DataAge()
        tar: DataAge()
        ti: DataAge()
        ts: DataAge()
        met: DataAge()
        roa: DataAge()
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.octet = 0
            self.gvr   = DataAge()
            self.gv    = DataAge()
            self.tar   = DataAge()
            self.ti    = DataAge()
            self.ts    = DataAge()
            self.met   = DataAge()
            self.roa   = DataAge()
            self.fx    = 0
        
        def add_info (self, item, info = str, count_octets = int):
            if self.octet[0] == '1':
                count_octets = self.gvr.add_info(self, info, count_octets)
            if self.octet[1] == '1':
                count_octets = self.gv.add_info(self, info, count_octets)
            if self.octet[2] == '1':
                count_octets = self.tar.add_info(self, info, count_octets)
            if self.octet[3] == '1':
                count_octets = self.ti.add_info(self, info, count_octets)
            if self.octet[4] == '1':
                count_octets = self.ts.add_info(self, info, count_octets)
            if self.octet[5] == '1':
                count_octets = self.met.add_info(self, info, count_octets)
            if self.octet[6] == '1':
                count_octets = self.roa.add_info(self, info, count_octets)
            if self.octet[7]:
                self.fx = self.octet[7]
            
            return count_octets
           
        def __str__(self, item):
            if self.exist:
                return (
                    f' GVR: {self.gvr}\n GV:  {self.gv}\n TAR: {self.tar}\n'
                    f' TI:  {self.ti}\n TS:  {self.ts}\n MET: {self.met}\n' 
                    f' ROA: {self.roa}\n' + item.octet_4.__str__(item))
            return "" 

    @dataclass        
    class Octet2:
        fl: DataAge()
        sal: DataAge()
        fsa: DataAge()
        asa: DataAge()
        tas: DataAge()
        mh: DataAge()
        bvr: DataAge()
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.octet = 0
            self.fl    = DataAge()
            self.sal   = DataAge()
            self.fsa   = DataAge()
            self.asa   = DataAge()
            self.tas   = DataAge()
            self.mh    = DataAge()
            self.bvr   = DataAge()
            self.fx    = 0
        
        def add_info (self, item, info = str, count_octets = int):
            if self.octet[0] == '1':
                count_octets = self.fl.add_info(self, info, count_octets)
            if self.octet[1] == '1':
                count_octets = self.sal.add_info(self, info, count_octets)
            if self.octet[2] == '1':
                count_octets = self.fsa.add_info(self, info, count_octets)
            if self.octet[3] == '1':
                count_octets = self.asa.add_info(self, info, count_octets)
            if self.octet[4] == '1':
                count_octets = self.tas.add_info(self, info, count_octets)
            if self.octet[5] == '1':
                count_octets = self.mh.add_info(self, info, count_octets)
            if self.octet[6] == '1':
                count_octets = self.bvr.add_info(self, info, count_octets)
            if self.octet[7]:
                self.fx = self.octet[7]
            
            return count_octets
        
        def __str__(self, item):
            if self.exist:
                return (
                    f' FL:  {self.fl}\n SAL: {self.sal}\n FSA: {self.fsa}\n'
                    f' AS:  {self.asa}\n TAS: {self.tas}\n MH:  {self.mh}\n' 
                    f' BVR: {self.bvr}\n' + item.octet_3.__str__(item))
            return "" 
    
    @dataclass        
    class Octet1:
        aos: DataAge()
        trd: DataAge()
        m3a: DataAge()
        qi: DataAge()
        ti: DataAge()
        mam: DataAge()
        gh: DataAge()
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.octet = 0
            self.aos   = DataAge()
            self.trd   = DataAge()
            self.m3a   = DataAge()
            self.qi    = DataAge()
            self.ti    = DataAge()
            self.mam   = DataAge()
            self.gh    = DataAge()
            self.fx    = 0
        
        def add_info (self, item, info = str, count_octets = int):
            if self.octet[0] == '1':
                count_octets = self.aos.add_info(self, info, count_octets)
            if self.octet[1] == '1':
                count_octets = self.trd.add_info(self, info, count_octets)
            if self.octet[2] == '1':
                count_octets = self.m3a.add_info(self, info, count_octets)
            if self.octet[3] == '1':
                count_octets = self.qi.add_info(self, info, count_octets)
            if self.octet[4] == '1':
                count_octets = self.ti.add_info(self, info, count_octets)
            if self.octet[5] == '1':
                count_octets = self.mam.add_info(self, info, count_octets)
            if self.octet[6] == '1':
                count_octets = self.gh.add_info(self, info, count_octets)
            if self.octet[7]:
                self.fx = self.octet[7]
            
            return count_octets
   
        def __str__(self, item):
            return (
                'Item295: Data Age\n'
                f' AOS: {self.aos}\n TRD: {self.trd}\n M3A: {self.m3a}\n'
                f' QI:  {self.qi}\n TI:  {self.ti}\n MAM: {self.mam}\n' 
                f' GH:  {self.gh}\n' + item.octet_2.__str__(item))      
   
    
    def __init__(self):
        self.exist   = False
        self.len     = 0
        self.hex     = 0
        self.octet_1 = self.Octet1()
        self.octet_2 = self.Octet2()
        self.octet_3 = self.Octet3()
        self.octet_4 = self.Octet4()
        self.fx      = 0  # There is no more documentacion about this FX
        
        
    def add_info(self, info = str, count_octets = int):
        aux_count_octets = count_octets
        lenght = 1
        info_item = info[count_octets*2:count_octets*2+lenght*2]
        res = "{0:08b}".format(int(info_item, 16))
        self.octet_1.octet = res
        self.octet_1.exist = True
        count_octets += lenght
        if res[7:] == '1':
            
            info_item = info[count_octets*2:count_octets*2+lenght*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.octet_2.octet = res
            self.octet_2.exist = True
            count_octets += lenght
            if res[7:] == '1':
            
                info_item = info[count_octets*2:count_octets*2+lenght*2]
                res = "{0:08b}".format(int(info_item, 16))
                self.octet_3.octet = res
                self.octet_3.exist = True
                count_octets += lenght
                if res[7:] == '1':
            
                    info_item = info[count_octets*2:count_octets*2+lenght*2]
                    res = "{0:08b}".format(int(info_item, 16))
                    self.octet_4.octet = res
                    self.octet_4.exist = True
                    count_octets += lenght
                    self.fx  = res[7:]
        
        if self.octet_1.exist:
            count_octets = self.octet_1.add_info(self, info, count_octets)
        
            if self.octet_2.exist:
                count_octets = self.octet_2.add_info(self, info, count_octets)
                
                if self.octet_3.exist:
                    count_octets = self.octet_3.add_info(self, info, count_octets)
                    
                    if self.octet_4.exist:
                        count_octets = self.octet_4.add_info(self, info, count_octets)      
        
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets 
    
    def __str__(self):
        return self.octet_1.__str__(self)
    
    
######################################################
@dataclass
class Item400:
    rid: int
    
    def __init__(self):
        self.exist = False
        self.len   = 1
        self.hex   = 0
        self.rid   = 0
        
    def add_info(self, info):
        self.hex = info
        self.rid = hexabin(info, 16)

    def __str__(self):
        return (
            f'Item400: Receiver ID\n'
            f' Receiver ID (RID): {self.rid}\n')


#################################################
###  Reserved Expansion Field implementation  ###
#################################################
@dataclass
class BPS:
    bps: int
    
    def __init__(self):
        self.exist = False
        self.len   = 2
        self.bps   = 0
                
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = hexabin(info_item, 16)
        self.exist = True 
        self.bps = res[4:]
        self.bps = int(self.bps, 2)*0.1
        count_octets += self.len            
        return count_octets
    
    def __str__(self):
        if self.exist:
            return (
                'Barometric Pressure Setting:\n'
                f' BPS: {self.bps}\n\n')
        return "" 
        
    
######################################################
@dataclass    
class SelH:
    hrd: int
    stat: int
    selh: int
    
    def __init__(self):
        self.exist = False
        self.len   = 2
        self.hrd   = 0
        self.stat  = 0
        self.selh  = 0

    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = hexabin(info_item, 16)
        self.exist = True 
        self.hrd = res[4:5]
        self.stat = res[5:6]
        self.selh = int(res[6:], 2)*0.703125
        count_octets += self.len
        
        return count_octets
    
    def __str__(self):
        if self.exist:
            return (
                f'Selected Heading:\n'
                f' HRD:  {self.hrd}\n'
                f' Stat: {self.stat}\n'
                f' SelH: {self.selh}\n\n')
        return "" 


######################################################
@dataclass
class NAV:
    ap: int
    vn: int
    ah: int
    am: int
    mfm: int
    
    def __init__(self):
        self.exist = False
        self.len   = 1
        self.ap    = 0
        self.vn    = 0
        self.ah    = 0
        self.am    = 0
        self.mfm   = 0

    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = hexabin(info_item, 16)
        self.exist = True 
        self.ap = res[:1]
        self.vn = res[1:2]
        self.ah = res[2:3]
        self.am = res[3:4]
        if res[4] == '1':
            self.mfm = res[5:6]
        count_octets += self.len
            
        return count_octets
        
    def __str__(self):
        if self.exist:
            return (
                'Navigation Mode:\n'
                f' AP:  {self.ap}\n'
                f' VN:  {self.vn}\n'
                f' AH:  {self.ah}\n'
                f' AM:  {self.am}\n'
                f' MFM: {self.mfm}\n\n')
        return "" 


######################################################
@dataclass
class GAO:
    lateral: int
    longitudinal: int
    
    def __init__(self):
        self.exist        = False
        self.len          = 1
        self.lateral      = 0
        self.longitudinal = 0
            
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = hexabin(info_item, 16)
        self.exist = True 
        self.lateral = int(res[:3], 2)*2
        self.longitudinal = int(res[3:])*2
        count_octets += self.len
        
        return count_octets

    def __str__(self):
        if self.exist:
            return (
                'GPS Antenna Offset:\n'
                f' Lateral:      {self.lateral}\n'
                f' Longitudinal: {self.longitudinal}\n\n')
        return "" 


######################################################
@dataclass
class SGV:    
    primary: 'SGV.Primary()'
    first_ext: 'SGV.FirstExt()'
    
    @dataclass
    class FirstExt:
        hgt: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.hgt   = 0
            self.fx    = 0
            
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.exist = True 
            self.hgt = int(res[:7], 2)*2.8125
            self.fx  = res[7:]
            count_octets += self.len
                
            return count_octets
        
        def __str__(self, item):
            if self.exist:
                return f' HGT: {self.hgt}\n'
            return "" 
    
    @dataclass
    class Primary:
        stp: int
        hts: int
        htt: int
        hrd: int
        gss: int

        def __init__(self):
            self.exist  = False
            self.len    = 2
            self.stp    = 0
            self.hts    = 0
            self.htt    = 0
            self.hrd    = 0
            self.gss    = 0
            self.fx     = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.exist = True 
            self.stp = res[:1]
            self.hts = res[1:2]
            self.htt = res[2:3]
            self.hrd = res[3:4]
            self.gss = int(res[4:17], 2)*0.125
            self.fx  = res[-1]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.first_ext.add_info(item, info, count_octets)
            return count_octets
        
        def __str__(self, item):
            return (
                f'Surface Ground Vector:\n'
                f' STP: {self.stp}\n'
                f' HTS: {self.hts}\n'
                f' HTT: {self.htt}\n'
                f' HRD: {self.hrd}\n'
                f' GSS: {self.gss}\n' + item.first_ext.__str__(item) + '\n')


    def __init__(self):
        self.exist      = False
        self.len        = 0
        self.primary    = self.Primary()
        self.first_ext  = self.FirstExt()
        
    def add_info(self, item, info = str, count_octets = int):
        self.exist = True
        count_octets = self.primary.add_info(self, info, count_octets)
        return count_octets

    def __str__(self):
        if self.exist:
            return self.primary.__str__(self)
        return ""

######################################################
@dataclass
class STA:
    primary: 'STA.Primary()'
    first_ext: 'STA.FirstExt()'
    second_ext: 'STA.SecondExt()'
    third_ext: 'STA.ThirdExt()'
    fourth_ext: 'STA.FourthExt()'
    fifth_ext: 'STA.FifthExt()'
    
    @dataclass
    class FifthExt:
        tao: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.tao   = 0
            self.fx    = 0  #No especifica uso de siguiente extensión
            
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))                
            self.exist = True 
            if res[:1] == '1':
                self.svh = res[1:6]
            self.fx  = res[-1]
            count_octets += self.len
            return count_octets
    
        def __str__(self, item):
            if self.exist:
                return f' TAO:  {self.tao}\n'
            return ""
    
    @dataclass
    class FourthExt:
        svh: int
        catc: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.svh   = 0
            self.catc  = 0
            self.fx    = 0
            
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.exist = True 
            if res[:1] == '1':
                self.svh = int(res[1:3], 2)
            if res[3:4] == '1':
                self.catc = int(res[4:7], 2)
            self.fx  = res[-1]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.fifth_ext.add_info(item, info, count_octets)                
            return count_octets 

        def __str__(self, item):
            if self.exist:
                return (
                    f' SVH:  {self.svh}\n'
                    f' CATC: {self.catc}\n'
                    + item.fifth_ext.__str__(item))
            return ""
        
    @dataclass
    class ThirdExt:
        daa: int
        df17ca: int
        
        def __init__(self):
            self.exist  = False
            self.len    = 1 
            self.daa    = 0
            self.df17ca = 0
            self.fx     = 0
            
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))                
            self.exist = True 
            if res[:1] == '1':
                self.daa = int(res[1:3], 2)
            if res[3:4] == '1':
                self.df17ca = int(res[4:7], 2)
            self.fx  = res[-1]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.fourth_ext.add_info(item, info, count_octets)                
            return count_octets   
        
        def __str__(self, item):
            if self.exist:
                return (
                    f' DAA:    {self.daa}\n'
                    f' DF17CA: {self.df17ca}\n'
                    + item.fourth_ext.__str__(item))
            return ""
        
    @dataclass
    class SecondExt:
        tsi: int
        muo: int
        rwc: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.tsi   = 0
            self.muo   = 0
            self.rwc   = 0
            self.fx    = 0
            
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))                
            self.exist = True 
            if res[:1] == '1':
                self.tsi = int(res[1:3], 2)
            if res[3:4] == '1':
                self.muo = int(res[4:5], 2)
            if res[5:6] == '1':
                self.rwc = int(res[6:7], 2)
            self.fx  = res[-1]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.third_ext.add_info(item, info, count_octets)                
            return count_octets
        
        def __str__(self, item):
            if self.exist:
                return (
                    f' TSI: {self.tsi}\n'
                    f' MUO: {self.muo}\n'
                    f' RWC: {self.rwc}\n'
                    + item.third_ext.__str__(item))
            return "" 

    @dataclass
    class FirstExt:
        ps3: int
        ptw: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.ps3   = 0
            self.ptw   = 0
            self.fx    = 0
            
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))                
            self.exist = True
            if res[:1] == '1':
                self.ps3 = int(res[1:4], 2)
            if res[4:5] == '1':
                self.tpw = int(res[5:7], 2)
            self.fx  = res[-1]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.second_ext.add_info(item, info, count_octets)                
            return count_octets
          
        def __str__(self, item):
            if self.exist:
                return (
                    f' PS3: {self.ps3}\n'
                    f' PTW: {self.ptw}\n'
                    + item.second_ext.__str__(item))
            return "" 
   
    @dataclass
    class Primary:
        es: int
        uat: int
        rce: int
        rrl: int

        def __init__(self):
            self.exist  = False
            self.len    = 1
            self.es     = 0
            self.uat    = 0
            self.rce    = 0
            self.rrl    = 0
            self.fx     = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))            
            self.exist = True 
            self.es = res[:1]
            self.uat = res[1:2]
            if res[2:3] == '1':
                self.rce = int(res[3:5], 2)
            if res[5:6] == '1':
                self.rrl = res[6:7]
            self.fx  = res[-1]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.first_ext.add_info(item, info, count_octets)
            return count_octets
        
        def __str__(self, item):
            return (
                f'Aircarft Status:\n'
                f' ES:  {self.es}\n'
                f' UAT: {self.uat}\n'
                f' RCE: {self.rce}\n'
                f' RRL: {self.rrl}\n'
                + item.first_ext.__str__(item) + '\n')


    def __init__(self):
        self.exist      = False
        self.len        = 0
        self.primary    = self.Primary()
        self.first_ext  = self.FirstExt()
        self.second_ext = self.SecondExt()
        self.third_ext  = self.ThirdExt()
        self.fourth_ext = self.FourthExt()
        self.fifth_ext  = self.FifthExt()
        
        
    def add_info(self, item, info = str, count_octets = int):
        self.exist = True
        count_octets = self.primary.add_info(self, info, count_octets)
        return count_octets
    
    def __str__(self):
        if self.exist:
            return self.primary.__str__(self)
        return ""
    
    
######################################################
@dataclass
class TNH:
    true_north_hea: int
    
    def __init__(self):
        self.exist          = False
        self.len            = 2
        self.true_north_hea = 0
            
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = hexabin(info_item, 16)        
        self.exist = True 
        self.true_north_hea = int(res, 2)*(360/pow(2,16))
        count_octets += self.len        
        return count_octets
    
    def __str__(self):
        if self.exist:
            return (
                'True North Heading:\n'
                f' TNH: {self.true_north_hea}\n\n')
        return "" 
    
    
######################################################
@dataclass
class MES:
    summ: 'MES.SUM()'
    pno: 'MES.PNO()'
    em1: 'MES.EM1()'
    xp: 'MES.XP()'
    fom: 'MES.FOM()'
    m2: 'MES.M2()'
    
    @dataclass
    class SUM:
        m5: int
        idd: int
        da: int
        m1: int
        m2: int
        m3: int
        mc: int
        po: int
    
        def __init__(self):
            self.exist = False
            self.len   = 1
            self.m5    = 0
            self.idd   = 0
            self.da    = 0
            self.m1    = 0
            self.m2    = 0
            self.m3    = 0
            self.mc    = 0
            self.po    = 0
                
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)            
            self.exist = True
            self.m5    = res[:1]
            self.id    = res[1:2]
            self.da    = res[2:3]
            self.m1    = res[3:4]
            self.m2    = res[4:5]
            self.m3    = res[5:6]
            self.mc    = res[6:7]
            self.po    = res[7:]
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    ' Mode 5 Summary:\n'
                    f'  M5: {self.m5}\n'
                    f'  ID: {self.id}\n'
                    f'  DA: {self.da}\n'
                    f'  M1: {self.m1}\n'
                    f'  M2: {self.m2}\n'
                    f'  M3: {self.m3}\n'
                    f'  MC: {self.mc}\n'
                    f'  PO: {self.po}\n\n')
            return ""
    
    @dataclass
    class PNO:
        pin: int
        no: int
    
        def __init__(self):
            self.exist = False
            self.len   = 4
            self.pin   = 0
            self.no    = 0
                
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)            
            self.exist = True
            self.pin   = res[2:16]
            self.no    = res[22:]
            count_octets += self.len            
            return count_octets

        def __str__(self):
            if self.exist:
                return (
                    ' Mode 5 PIN / National Origin:\n'
                    f'  PIN: {self.pin}\n'
                    f'  NO:  {self.no}\n\n')
            return ""        
        
    @dataclass    
    class EM1:
        v: int
        l: int
        em1: int
    
        def __init__(self):
            self.exist = False
            self.len   = 2
            self.v     = 0
            self.l     = 0
            self.em1   = 0
                
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)
            self.exist = True
            self.v   = res[:1]
            self.l   = res[2:3]
            self.em1 = oct(int(res[4:], 2))
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    ' Extended Mode 1 Code:\n'
                    f'  V:   {self.v}\n'
                    f'  L:   {self.l}\n'
                    f'  EM1: {self.m1}\n\n')
            return ""
    
    @dataclass
    class XP:
        xp: int
        x5: int
        xc: int
        x3: int
        x2: int
        x1: int
    
        def __init__(self):
            self.exist = False
            self.len   = 1
            self.xp    = 0
            self.x5    = 0
            self.xc    = 0
            self.x3    = 0
            self.x2    = 0
            self.x1    = 0
                
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)            
            self.exist = True
            self.xp    = res[2:3]
            self.x5    = res[3:4]
            self.xc    = res[4:5]
            self.x3    = res[5:6]
            self.x2    = res[6:7]
            self.x1    = res[7:]
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    ' X Oulse Presence:\n'
                    f'  XP: {self.xp}\n'
                    f'  X5: {self.x5}\n'
                    f'  XC: {self.xc}\n'
                    f'  X3: {self.x3}\n'
                    f'  X2: {self.x2}\n'
                    f'  X1: {self.x1}\n\n')
            return ""
        
    @dataclass    
    class FOM:
        fom: int
    
        def __init__(self):
            self.exist = False
            self.len   = 1
            self.fom   = 0
                
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)            
            self.exist = True
            self.fom   = res[3:]
            count_octets += self.len            
            return count_octets 

        def __str__(self):
            if self.exist:
                return (
                    ' Figure of Merit:\n'
                    f'  FOM: {self.fom}\n\n')
            return ""        
    
    @dataclass
    class M2:
        v: int
        l: int
        m2: int
    
        def __init__(self):
            self.exist = False
            self.len   = 2
            self.v     = 0
            self.l     = 0
            self.m2    = 0
                
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)            
            self.exist = True
            self.v   = res[:1]
            self.l   = res[2:3]
            self.em2 = oct(int(res[4:], 2))
            count_octets += self.len            
            return count_octets  
        
        def __str__(self):
            if self.exist:
                return (
                    ' Mode 2 Code:\n'
                    f'  V:   {self.v}\n'
                    f'  L:   {self.l}\n'
                    f'  M2:  {self.m2}\n\n')
            return ""
        
        
    def __init__(self):
        self.exist = False
        self.len   = 1 
        self.octet = 0
        self.summ  = self.SUM()
        self.pno   = self.PNO()
        self.em1   = self.EM1()
        self.xp    = self.XP()
        self.fom   = self.FOM()
        self.m2    = self.M2()
        self.fx    = 0
    
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = "{0:08b}".format(int(info_item, 16))
        self.exist = True
        self.octet = res
        self.fx = res[-1]
        count_octets += self.len
        
        if self.octet[0] == '1':
            count_octets = self.summ.add_info(self, info, count_octets)
        if self.octet[1] == '1':
            count_octets = self.pno.add_info(self, info, count_octets)
        if self.octet[2] == '1':
            count_octets = self.em1.add_info(self, info, count_octets)
        if self.octet[3] == '1':
            count_octets = self.xp.add_info(self, info, count_octets)
        if self.octet[4] == '1':
            count_octets = self.fom.add_info(self, info, count_octets)
        if self.octet[5] == '1':
            count_octets = self.m2.add_info(self, info, count_octets)
                    
        return count_octets
    
    def __str__(self):
        if self.exist:
            return (
                ' Military Extended Squitter\n'
                f'{self.sum}{self.pno}{self.em1}'
                f'{self.cp}{self.fom}{self.m2}\n\n')
        return ""
    
    
######################################################
@dataclass
class RE:
    data: 'RE.Data()'
    
    @dataclass
    class Data:
        bps: BPS()
        selh: SelH()
        nav: NAV()
        gao: GAO()
        sgv: SGV()
        sta: STA()
        tnh: TNH()
        mes: MES()
    
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.octet = 0
            self.bps   = BPS()
            self.selh  = SelH()
            self.nav   = NAV()
            self.gao   = GAO()
            self.sgv   = SGV()
            self.sta   = STA()
            self.tnh   = TNH()
            self.mes   = MES()
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.exist = True
            self.octet = res
            count_octets += self.len
            
            if self.octet[0] == '1':
                count_octets = self.bps.add_info(self, info, count_octets)
            if self.octet[1] == '1':
                count_octets = self.selh.add_info(self, info, count_octets)
            if self.octet[2] == '1':
                count_octets = self.nav.add_info(self, info, count_octets)
            if self.octet[3] == '1':
                count_octets = self.gao.add_info(self, info, count_octets)
            if self.octet[4] == '1':
                count_octets = self.sgv.add_info(self, info, count_octets)
            if self.octet[5] == '1':
                count_octets = self.sta.add_info(self, info, count_octets)
            if self.octet[6] == '1':
                count_octets = self.tnh.add_info(self, info, count_octets)
            if self.octet[7] == '1':
                count_octets = self.mes.add_info(self, info, count_octets)
            
            return count_octets
        
        def __str__(self, item):
            return (
                'RE: Reserved Expansion Field\n'
                f'{self.bps}{self.selh}{self.nav}'
                f'{self.gao}{self.sgv}{self.sta}' 
                f'{self.tnh}{self.mes}\n')
   
    
    def __init__(self):
        self.exist           = False
        self.len             = 0
        self.hex             = 0
        self.len_indicator   = 0
        self.data            = self.Data()
        
    def add_info(self, info = str, count_octets = int):
        aux_count_octets = count_octets
        lenght = 1
        self.len_indicator = info[count_octets*2:count_octets*2+lenght*2]
        #aux_count = count_octets + int(self.len_indicator,16)
        count_octets += lenght
        count_octets = self.data.add_info(self, info, count_octets)
        
        self.hex = info[aux_count_octets*2:count_octets*2]
        #if count_octets == aux_count:
        #    print("----CORRECT READ LENGTH----")
            
        return count_octets

    def __str__(self):
        return self.data.__str__(self)


######################################################
@dataclass
class ItemNotUsed:
    
    def __init__(self):
        self.exist           = False
        self.len             = 0   
        self.hex             = 0
        
    def __str__(self, item):
        return 'Item not used\n\n'
    
    
######################################################
@dataclass
class BlockCat21:
    fspec: int 
    item010: Item010()
    item040: Item040()
    item161: Item161()
    item015: Item015()
    item071: Item071()
    item130: Item130()
    item131: Item131()
    item072: Item072()
    item150: Item150()
    item151: Item151()
    item080: Item080()
    item073: Item073()
    item074: Item074()
    item075: Item075()
    item076: Item076()
    item140: Item140()
    item090: Item090()
    item210: Item210()
    item070: Item070()
    item230: Item230()
    item145: Item145()
    item152: Item152()
    item200: Item200()
    item155: Item155()
    item157: Item157()
    item160: Item160()
    item165: Item165()
    item077: Item077()
    item170: Item170()
    item020: Item020()
    item220: Item220()
    item146: Item146()
    item148: Item148()
    item110: Item110()
    item016: Item016()
    item008: Item008()
    item271: Item271()
    item132: Item132()
    item250: Item250()
    item260: Item260()
    item400: Item400()
    item295: Item295()
    re     : RE()
    sp     : ItemNotUsed()
    
    def __init__(self):
        self.fspec   = 0
        self.item010 = Item010()
        self.item040 = Item040()
        self.item161 = Item161()
        self.item015 = Item015()
        self.item071 = Item071()
        self.item130 = Item130()
        self.item131 = Item131()
        self.item072 = Item072()
        self.item150 = Item150()
        self.item151 = Item151()
        self.item080 = Item080()
        self.item073 = Item073()
        self.item074 = Item074()
        self.item075 = Item075()
        self.item076 = Item076()
        self.item140 = Item140()
        self.item090 = Item090()
        self.item210 = Item210()
        self.item070 = Item070()
        self.item230 = Item230()
        self.item145 = Item145()
        self.item152 = Item152()
        self.item200 = Item200()
        self.item155 = Item155()
        self.item157 = Item157()
        self.item160 = Item160()
        self.item165 = Item165()
        self.item077 = Item077()
        self.item170 = Item170()
        self.item020 = Item020()
        self.item220 = Item220()
        self.item146 = Item146()
        self.item148 = Item148()
        self.item110 = Item110()
        self.item016 = Item016()
        self.item008 = Item008()
        self.item271 = Item271()
        self.item132 = Item132()
        self.item250 = Item250()
        self.item260 = Item260()
        self.item400 = Item400()
        self.item295 = Item295()
        self.frn43   = ItemNotUsed()
        self.frn44   = ItemNotUsed()
        self.frn45   = ItemNotUsed()
        self.frn46   = ItemNotUsed()
        self.frn47   = ItemNotUsed()
        self.re      = RE()
        self.sp      = ItemNotUsed()
    

    def add_items(self, info: str, count_octets: int, message_info):
        nombres_atributos = list(self.__dict__.keys())
        i = 0
        for nombre in nombres_atributos[1:]:
            if self.fspec[i] != '0':
                valor_item = getattr(self, nombre)
                if valor_item.len > 0:
                    info_item = info[count_octets*2:count_octets*2+valor_item.len*2]
                    valor_item.add_info(info_item)
                    count_octets += valor_item.len
                else:
                    count_octets = valor_item.add_info(info, count_octets)
                message_info.modify_count(count_octets)        
            #else:
            #    print("_______________________________________")
            #    print("ITEM NO INCLUIDO00: {}".format(nombre))  
            i += 1
            if i >= len(self.fspec):
                break
        return count_octets
        
    
    def modify_exist(self, fspec):       
        # Get item names of instance
        nombres_atributos = list(self.__dict__.keys())
        i = 0
        for nombre in nombres_atributos[1:]:
            if fspec[i] != '0':
                valor_actual = getattr(self, nombre)
                setattr(valor_actual, 'exist', True)
            #else:
            #  print("ITEM NO INCLUIDO-O: {}".format(nombre))  
            i += 1
            if i >= len(fspec):
                break


    def check_fspec(self, line, count_octets):
        fspec = ""
        while True:
            octet = line[count_octets*2:count_octets*2+2]
            count_octets += 1
            res = "{0:08b}".format(int(octet, 16))
            final = res[7]
            fspec += res[0:7]
            if final != '1':
                break
        return fspec, count_octets
    

    def add_fspec(self, fspec):
        self.fspec = fspec
        self.modify_exist(fspec)
        
        
    def add_block(self, info, count, message_info):
        fspec, count_octets = self.check_fspec(info, count)
        self.add_fspec(fspec)
        count_octets = self.add_items(info, count_octets, message_info)
        return count_octets
        
        
    def print_info_debbug(self):     
        # Obtener los nombres de los atributos de la instancia
        str_info = ""
        nombres_atributos = list(self.__dict__.keys())
        # Iterar sobre los atributos en el orden de declaración
        print("Valor actual:", nombres_atributos)
        print("\n----------------------------\n")
        for nombre in nombres_atributos[1:]:
            valor_actual = getattr(self, nombre)
            #print("Valor actual:", valor_actual)
            if valor_actual.exist: 
                print("ITEM INCLUIDO: {}".format(nombre))
                print(valor_actual)
                str_info += str(valor_actual) + "\n"
            else:
                print("ITEM NO INCLUIDO: {}".format(nombre))  
            print("\n----------------------------\n")
        #print("STR_INFO: {}".format(str_info))
        return str_info
    
    
    def print_info(self):     
        str_info = ""
        nombres_atributos = list(self.__dict__.keys())
        for nombre in nombres_atributos[1:]:
            valor_actual = getattr(self, nombre)
            if valor_actual.exist: 
                str_info += str(valor_actual) + "\n"
        return str_info
    
    
    def __str__(self):
        return (self.print_info())


##############################################################################
@dataclass
class AsterixMessage:
    cat: int
    leng: int
    info: int
    count: int
    blocks: []
    
    
    def __init__(self, cat: int, length: int, info: str, count: int):
        self.cat = cat
        self.leng = length
        self.info = info
        self.count = count
        self.blocks = []
        
        
    def modify_count(self, count_octets):
        self.count = count_octets
        
        
    def add_blocks(self):
        # Add new BlockCat21 instance to blocks list
        new_block = BlockCat21()
        self.blocks.append(new_block)
        try:
            i = 0
            while self.count < self.leng:
                count_octets = self.blocks[i].add_block(self.info, self.count, self)
                self.modify_count(count_octets)
                i += 1
        except IndexError as e:
            print("-----------------------------")
            print(f"Error: {e}")
            print("-----------------------------")
            
        
    def __str__(self):
        data = ""
        for message_data in self.blocks:
            data += (message_data.print_info() + "\n" + 
                     '********************************************\n\n')
        
        return ('********************************************\n'
                '*******   Decoded ASTERIX Message:   *******\n'
                '********************************************\n\n'
                f'{self.info}\n' 
                '********************************************\n\n'
                + data)
    

##############################################################################
@dataclass
class Category21:
    count: int
    messages: []
    
    
    def __init__(self):
        self.count = 0
        self.messages = []
        
        
    def add_message(self, cat: int, length: int, info: str, count: int, num_message: int):
        new_message = AsterixMessage(cat, length, info, count)
        self.messages.append(new_message)
        self.messages[num_message].add_blocks()
        
        
    def add_count(self):
        self.count += 1
        
    
##############################################################################    
