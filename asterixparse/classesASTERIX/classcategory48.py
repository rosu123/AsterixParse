#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 19:51:30 2024

@author: rodrigo
"""

import inspect
import math
import json

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

from . import classmodes


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
            raise ValueError("Item010: value out of range\n")
        
    def __str__(self):
        return (
            f'Item010: Data Source Identification\n SAC: {self.sac}\n'
            f' SIC: {self.sic}\n')
                

######################################################        
@dataclass
class Item020:
    primary: 'Item020.Primary()'
    first_ext: 'Item020.FirstExt()'
    second_ext: 'Item020.SecondExt()'
    
    @dataclass    
    class SecondExt:
        adsb: int
        scn: int
        pai: int
        spare: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.adsb  = 0
            self.scn   = 0
            self.pai   = 0
            self.spare = 0
            self.fx    = 0
            
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))            
            self.exist = True 
            self.adbs = res[0:2]
            self.scn = res[2:4]
            self.pai = res[4:6]
            self.spare = res[6:7]
            self.fx  = res[7:]
            count_octets += self.len
         
        def __str__(self, item):
            if self.exist:
                return (
                    f' ADS-B populated (ADS-B): {self.adsb[0]}\n'
                    f'    On-Side ADS-B Inforation: {self.adsb[1]}\n'
                    f' SCN populated (SCN): {self.scn[0]}\n'
                    f'    Surveillance Cluster Network Information: {self.scn[1]}\n'
                    f' PAI populated (PAI): {self.pai[0]}\n'
                    f'    Passive Acquisition Interface Information: {self.pai[1]}\n')
            return ""
    
    @dataclass        
    class FirstExt:
        tst: int
        err: int
        xpp: int
        me: int
        mi: int
        foe_fri: int
        
        def __init__(self):
            self.exist   = False
            self.len     = 1 
            self.tst     = 0
            self.err     = 0
            self.xpp     = 0
            self.me      = 0
            self.mi      = 0
            self.foe_fri = 0
            self.fx      = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))            
            self.exist = True 
            self.tst = res[:1]
            self.err = res[1:2]
            self.xpp = res[2:3]
            self.me = res[3:4]
            self.mi = res[4:5]
            self.foe_fri = res[5:7]
            self.fx  = res[7:]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.second_ext.add_info(item, info, count_octets)
            return count_octets
        
        def __str__(self, item):
            if self.exist:
                return (
                    f' Test Target Report (TST): {self.tst}\n'
                    f' Extended Range (ERR): {self.err}\n'
                    f' X-Pulse (XPP): {self.xpp}\n'
                    f' Military Emergency (ME): {self.me}\n'
                    f' Military ID (MI): {self.mi}\n'
                    f' FOE/FRI: {self.foe_fri}\n'+ item.second_ext.__str__(item))
            return ""
  
    @dataclass
    class Primary:
        typ: int
        sim: int
        rdp: int
        spi: int
        rab: int
 
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.typ   = 0
            self.sim   = 0
            self.rdp   = 0
            self.spi   = 0
            self.rab   = 0
            self.fx    = 0
            
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))            
            self.exist = True 
            self.typ = res[:3]
            self.sim = res[3:4]
            self.rdp = res[4:5]
            self.spi = res[5:6]
            self.rab = res[6:7]
            self.fx  = res[7:]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.first_ext.add_info(item, info, count_octets)
            return count_octets
        
        def __str__(self, item):
            return (
                f'Item020: Target Report Descriptor\n'
                f' Type (TYP): {self.typ}\n'
                f' Simulated target report (SIM): {self.sim}\n'
                f' Special Position Identification (SPI): {self.spi}\n'
                f' Report (RAB): {self.rab}\n' + item.first_ext.__str__(item))
                
            
    def __init__(self):
        self.exist      = False
        self.len        = 0
        self.hex        = 0
        self.primary    = self.Primary()
        self.first_ext  = self.FirstExt()
        self.second_ext = self.SecondExt()
        
    def add_info(self, info = str, count_octets = int):
        aux_count_octets = count_octets
        count_octets = self.primary.add_info(self, info, count_octets)
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets
    
    def __str__(self):
        return self.primary.__str__(self)
   

######################################################        
@dataclass
class Item030:
    primary: 'Item030.Primary()'
    first_ext: 'Item030.FirstExt()'
    
    @dataclass        
    class FirstExt:
        code: int        
        
        def __init__(self):
            self.exist = False
            self.len   = 1
            self.code  = 0
            self.fx    = 0  # There is no more documentacion about this FX
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.exist = True 
            self.code = int(res[:7], 2)
            self.fx = res[7:]
            count_octets += self.len
        
        def __str__(self, item):
            if self.exist:
                return f' Code: {self.code}\n'
            return ""
    
    @dataclass
    class Primary:
        code: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1
            self.code  = 0
            self.fx    = 0
            
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))            
            self.exist = True 
            self.code = int(res[:7], 2)
            self.fx = res[7:]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.first_ext.add_info(item, info, count_octets)
            return count_octets
        
        def __str__(self, item):
            return (
                f'Item030: Warning/Error Conditions and Target Classification\n'
                f' Code: {self.code}\n' + item.first_ext.__str__(item))
                
        
    def __init__(self):
        self.exist      = False
        self.len        = 0
        self.hex        = 0
        self.primary    = self.Primary()
        self.first_ext  = self.FirstExt()
        
    def add_info(self, info = str, count_octets = int):
        aux_count_octets = count_octets
        count_octets = self.primary.add_info(self, info, count_octets)
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets
    
    def __str__(self):
        return self.primary.__str__(self)


######################################################        
@dataclass       
class Item040:
    rho: int
    theta: int
    
    def __init__(self):
        self.exist = False
        self.len   = 4
        self.hex   = 0
        self.rho   = 0
        self.theta = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.rho = int(res[:16], 2)*(1/256)
        self.theta = int(res[16:], 2)*(360/pow(2,16))
        
    def __str__(self):
        return (
            f'Item040: Measured Position in Polar Co-ordinates\n'
            f' RHO: {self.rho}\n'
            f' THETA: {self.theta}\n')


######################################################
@dataclass
class Item042:
    x: int
    y: int
    
    def __init__(self):
        self.exist = False
        self.len   = 4
        self.hex   = 0
        self.x     = 0
        self.y     = 0

    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.x = twos_comp(int(res[:16], 2), len(res[:15]))/128
        self.y = twos_comp(int(res[16:], 2), len(res[15:]))/128
        
    def __str__(self):
        return (
            f'Item042: Calculated Position in Cartesian Co-ordinates\n'
            f' X-Component: {self.x}\n'
            f' Y-Component: {self.y}\n')
        
    
######################################################
@dataclass
class Item050:
    v: int
    g: int
    l: int
    mode2: int
    
    def __init__(self):
        self.exist  = False
        self.len    = 2
        self.hex    = 0
        self.v      = 0
        self.g      = 0
        self.l      = 0
        self.mode2  = 0
      
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)        
        self.v = res[:1]
        self.g = res[1:2]
        self.l = res[2:3]
        # Convert str bin to int, then to octal
        aux = oct(int(res[4:], 2))
        #Get rid from the initial "0o"
        self.mode2 = aux[2:]
        
    def __str__(self):
        return (
            f'Item050: Mode-2 Code in Octal Representation\n'
            f' V: {self.v} | G: {self.g} | L: {self.l}\n'
            f' Mode-2 code: {self.mode2}\n')


######################################################       
@dataclass        
class Item055:
    v: int
    g: int
    l: int
    mode1: int
    
    def __init__(self):
        self.exist  = False
        self.len    = 1
        self.hex    = 0
        self.v      = 0
        self.g      = 0
        self.l      = 0
        self.mode1  = 0
      
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)        
        self.v = res[:1]
        self.g = res[1:2]
        self.l = res[2:3]
        # Convert str bin to int, then to octal
        aux = oct(int(res[3:], 2))
        #Get rid from the initial "0o"
        self.mode1 = aux[2:]
        
    def __str__(self):
        return (
            f'Item055: Mode-1 Code in Octal Representation\n'
            f' V: {self.v} | G: {self.g} | L: {self.l}\n'
            f' Mode-1 code: {self.mode1}\n')
    
    
######################################################
@dataclass
class Item060:
    qxi: int
    
    def __init__(self):
        self.exist = False
        self.len   = 2
        self.hex   = 0
        self.spare = 0
        self.qxi   = 0
      
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.spare = res[:4]
        self.qxi = res[4:]
        
    def __str__(self):
        return (
            f'Item060: Mode-2 Code Confidence Indicator\n'
            f' Quality of the pulse (QXi): {self.qxi}\n')


######################################################
@dataclass
class Item065:
    qxi: int
    
    def __init__(self):
        self.exist = False
        self.len   = 1
        self.hex   = 0
        self.spare = 0
        self.qxi   = 0
      
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.spare = res[:3]
        self.qxi = res[3:]
        
    def __str__(self):
        return (
            f'Item065: Mode-1 Code Confidence Indicator\n'
            f' Quality of the pulse (QXi): {self.qxi}\n')
    
    
######################################################
@dataclass
class Item070:
    v: int
    g: int
    l: int
    mode3_a: int
    
    def __init__(self):
        self.exist   = False
        self.len     = 2
        self.hex     = 0
        self.v       = 0
        self.g       = 0
        self.l       = 0
        self.mode3_a = 0
      
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)        
        self.v = res[:1]
        self.g = res[1:2]
        self.l = res[2:3]
        # Convert str bin to int, then to octal
        aux = oct(int(res[4:], 2))
        #Get rid from the initial "0o"
        self.mode3_a = aux[2:]
        
    def __str__(self):
        return (
            f'Item070: Mode-3/A Code in Octal Representation\n'
            f' V: {self.v} | G: {self.g} | L: {self.l}\n'
            f' Mode-3/A code: {self.mode3_a}\n')

    
######################################################
@dataclass
class Item080:
    qxi: int
    
    def __init__(self):
        self.exist = False
        self.len   = 2
        self.hex   = 0
        self.spare = 0
        self.qxi   = 0
      
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.spare = res[:4]
        self.qxi = res[4:]
        
    def __str__(self):
        return (
            f'Item080: Mode-3/A Code Confidence Indicator\n'
            f' Quality of the pulse (QXi): {self.qxi}\n')
    
    
######################################################
@dataclass
class Item090:
    v: int
    g: int
    bina: int
    fl: int
    
    def __init__(self):
        self.exist  = False
        self.len    = 2
        self.hex    = 0
        self.v      = 0
        self.g      = 0
        self.bina   = 0
        self.fl     = 0
      
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)        
        self.v = res[:1]
        self.g = res[1:2]
        self.bina = res[2:]
        self.fl = int(res[2:],2)*(1/4)
        
    def __str__(self):
        return (
            f'Item090: Flight Level in Binary Repr.\n'
            f' V: {self.v} | G: {self.g}\n'
            f' Flight Level (FL): {self.fl}\n')


######################################################       
@dataclass
class Item100:
    v: int
    g: int
    mode_c: int
    qxi: int
    
    def __init__(self):
        self.exist  = False
        self.len    = 4
        self.hex    = 0
        self.v      = 0
        self.g      = 0
        self.mode_c = 0
        self.qxi    = 0
      
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)        
        self.v = res[:1]
        self.g = res[1:2]
        self.mode_c = res[4:16]
        self.qxi = res[20:]
        
    def __str__(self):
        return (
            f'Item100: Mode-C Code and Code Confidence Indicator\n'
            f' V: {self.v} | G: {self.g}\n'
            f' Mode-C code (Gray notation): {self.mode_c}\n'
            f' Quality of the pulse (QXi): {self.qxi}\n')
 
        
######################################################
@dataclass
class Item110:
    height_3d: int
   
    def __init__(self):
        self.exist     = False
        self.len       = 2
        self.hex       = 0
        self.height_3d = 0
      
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.height_3d = twos_comp(int(res[2:], 2), len(res[2:]))*25
        
    def __str__(self):
        return (
            f'Item110: Height Measured by 3D Radar\n'
            f' 3D-Height: {self.height_3d}\n')


######################################################
# CHECK if the blocks are added correctly and if they are printed correctly 
# (I have not found example with this item)
@dataclass
class Item120:
    cal: 'Item120.CAL()'
    rds: 'Item120.RepRDS()'
    
    @dataclass
    class RDS:
        dop:int
        amb: int
        frq: int
        
        def __init__(self):
            self.len = 6
            self.dop = 0
            self.amb = 0
            self.frq = 0
        
        def add_info (self, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)
            self.exist = True 
            self.dop = int(res[:16], 2)
            self.amb = int(res[16:32], 2)
            self.frq = int(res[32:], 2)
            count_octets += self.len            
            return count_octets
     
        def __str__(self):
            return (
                f' Doppler Speed: {self.dop}\n'
                f' Ambiguity Range: {self.amb}\n'
                f' Transmitter Frequency: {self.frq}\n')
    
    @dataclass
    class RepRDS:
        #rep: int
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
                new_block = self.RDS()
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
    class CAL:
        d: int
        cal: int
        
        def __init__(self):
            self.exist = False
            self.len   = 2 
            self.d     = 0
            self.cal   = 0
            self.spare = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)
            self.exist = True 
            self.d = res[:1]
            self.cal = twos_comp(int(res[6:], 2), len(res[6:]))*1
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    f' Doppler speed valid: {self.d}\n'
                    f' Calculated Doppler Speed: {self.cal}\n')
            return ""
   
    
    def __init__(self):
        self.exist = False
        self.len   = 0
        self.hex   = 0
        self.cal   = self.CAL()
        self.rds   = self.RepRDS()
        self.spare = 0
        self.fx    = 0  # There is no more documentacion about this FX
        
    def add_info(self, info = str, count_octets = int):
        lenght = 1
        aux_count_octets = count_octets
        info_item = info[count_octets*2:count_octets*2+lenght*2]
        res = "{0:08b}".format(int(info_item, 16))
        count_octets += lenght
        if res[:1] == '1':
            count_octets = self.cal.add_info(self, info, count_octets)
        if res[1:2] == '1':
            count_octets = self.rds.add_blocks(self, info, count_octets)
        self.fx = res[7:]
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets    
            
    def __str__(self):
        return (
            f'Item120: Radial Doppler Speed\n{self.cal}\n{self.rds}\n')


######################################################
@dataclass    
class Item130:
    srl: 'Item130.SRL()'
    srr: 'Item130.SRR()'
    sam: 'Item130.SAM()'
    prl: 'Item130.PRL()'
    pam: 'Item130.PAM()'
    rpd: 'Item130.RPD()'
    apd: 'Item130.APD()'
    
    @dataclass
    class APD():
        apd: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.apd   = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)
            self.exist = True 
            self.apd = twos_comp(int(res, 2), len(res))*(360/pow(2,14))
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    f' Difference in Azimuth PSR-SSR (APD): {self.apd}\n')
            return ""
    
    @dataclass
    class RPD():
        rpd: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.rpd   = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)
            self.exist = True 
            self.rpd = twos_comp(int(res, 2), len(res))*(1/256)
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    f' Range PSR-SSR (RPD): {self.rpd}\n')
            return ""
    
    @dataclass 
    class PAM():
        pam: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.pam   = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)
            self.exist = True 
            self.pam = twos_comp(int(res, 2), len(res))*1
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    f' Amplitude of Primary Plot (PAM): {self.pam}\n')
            return ""
        
    @dataclass
    class PRL():
        prl: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.prl   = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = int(info_item, 16)            
            self.exist = True 
            self.prl = res*(360/pow(2,13))
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    f' Primary Plot Runlegth (PRL): {self.prl}\n')
            return ""
          
    @dataclass    
    class SAM():
        sam: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.sam   = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = int(info_item, 16)            
            self.exist = True 
            self.sam = res*1
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    f' Amplitude of (M)SSR reply (SAM): {self.sam}\n')
            return ""
         
    @dataclass        
    class SRR():
        srr: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.srr   = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = int(info_item, 16)            
            self.exist = True 
            self.srr = res*1
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    f' Number of Received Replies for (M)SSR (SRR): {self.srr}\n')
            return ""
            
    @dataclass        
    class SRL():
        srl: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.srl   = 0
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = int(info_item, 16)            
            self.exist = True 
            self.srl = res*(360/pow(2,13))
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    f' SSR Plot Runlength (SRL): {self.srl}\n')
            return ""
   
            
    def __init__(self):
        self.exist = False
        self.len   = 0
        self.hex   = 0
        self.srl   = self.SRL()
        self.srr   = self.SRR()
        self.sam   = self.SAM()
        self.prl   = self.PRL()
        self.pam   = self.PAM()
        self.rpd   = self.RPD()
        self.apd   = self.APD()
        self.fx    = 0  # There is no more documentacion about this FX
        
        
    def add_info(self, info = str, count_octets = int):
        aux_count_octets = count_octets
        lenght = 1 
        info_item = info[count_octets*2:count_octets*2+lenght*2]
        res = "{0:08b}".format(int(info_item, 16))
        count_octets += lenght
        
        if res[:1] == '1':
            count_octets = self.srl.add_info(self, info, count_octets)
        if res[1:2] == '1':
            count_octets = self.srr.add_info(self, info, count_octets)
        if res[2:3] == '1':
            count_octets = self.sam.add_info(self, info, count_octets)
        if res[3:4] == '1':
            count_octets = self.prl.add_info(self, info, count_octets)
        if res[4:5] == '1':
            count_octets = self.pam.add_info(self, info, count_octets)
        if res[5:6] == '1':
            count_octets = self.rpd.add_info(self, info, count_octets)
        if res[6:7] == '1':
            count_octets = self.apd.add_info(self, info, count_octets)
        
        self.fx = res[7:]
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets
        
    def __str__(self):
        return (
            f'Item130: Radar Plot Characteristics\n'
            f'{self.srl}{self.srr}{self.sam}{self.prl}\n'
            f'{self.pam}{self.rpd}{self.apd}\n')
  
    
######################################################        
@dataclass
class Item140:
    time_of_day: int
    
    def __init__(self):
        self.exist       = False
        self.len         = 3
        self.hex         = 0
        self.time_of_day = 0
      
    def add_info(self, info):
        self.hex = info
        self.time_of_day = int(hexabin(info, 16), 2)/128
        
    def __str__(self):
        delta = timedelta(seconds=self.time_of_day)
        midnight = datetime(1, 1, 1, 0, 0, 0)
        date_time = midnight + delta
        
        return (
            f'Item140: Time of Day\n'
            f' Time of Day: {self.time_of_day}\n'
            " Time format: {:02d}:{:02d}:{:02d},{:06d}\n".format(date_time.hour, 
              date_time.minute, date_time.second, date_time.microsecond))
    

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
class Item170:
    primary: 'Item170.Primary()'
    first_ext: 'Item170.FirstExt()'
    
    @dataclass        
    class FirstExt:
        tre: int
        gho: int
        sup: int
        tcc: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1
            self.tre   = 0
            self.gho   = 0
            self.sup   = 0
            self.tcc   = 0
            self.fx    = 0  # There is no more documentacion about this FX
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.exist = True 
            self.tre = res[:1]
            self.gho = res[1:2]
            self.sup = res[2:3]
            self.tcc = res[3:4]
            self.fx = res[7:]
            count_octets += self.len
            return count_octets
        
        def __str__(self, item):
            if self.exist:
                return (
                    f' Signal End_of_Track (TRE): {self.tre}\n'
                    f' Ghost vs. True Target (GHO): {self.gho}\n'
                    f' Track maintained with Node B (SUP): {self.sup}n'
                    f' Type of plot coord. transfor. mechanism (TCC): {self.tcc}\n')
            return ""
   
    @dataclass
    class Primary:
        cnf: int
        rad: int
        dou: int
        mah: int
        cdm: int
        
        def __init__(self):
            self.exist = False
            self.len   = 1
            self.cnf   = 0
            self.rad   = 0
            self.dou   = 0
            self.mah   = 0
            self.cdm   = 0
            self.fx    = 0
            
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.exist = True 
            self.cnf = res[:1]
            self.rad = res[1:3]
            self.dou = res[3:4]
            self.mah = res[4:5]
            self.cdm = res[5:7]
            self.fx = res[7:]
            count_octets += self.len
            if self.fx == '1':
                count_octets = item.first_ext.add_info(item, info, count_octets)
            return count_octets
        
        def __str__(self, item):
            return (
                f'Item170: Track Status\n'
                f' Confirmed vs. Tentative Track (CNF): {self.cnf}\n'
                f' Type of Sensor(s) maintaining Track (RAD): {self.rad}\n'
                f' Signal level confidence (DOU): {self.dou}\n'
                f' Manoeuvre det. in Horizontal Sense (MAH): {self.mah}\n' 
                + item.first_ext.__str__(item))
                
            
    def __init__(self):
        self.exist      = False
        self.len        = 0
        self.hex        = 0
        self.primary    = self.Primary()
        self.first_ext  = self.FirstExt()
        
    def add_info(self, info = str, count_octets = int):
        aux_count_octets = count_octets
        count_octets = self.primary.add_info(self, info, count_octets)
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets
    
    def __str__(self):
        return self.primary.__str__(self)


######################################################
@dataclass
class Item200:
    ground_speed: int
    heading: int
    
    def __init__(self):
        self.exist        = False
        self.len          = 4
        self.hex          = 0
        self.ground_speed = 0
        self.heading      = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.ground_speed = int(res[:16], 2)*pow(2,-14)
        self.heading = int(res[16:], 2)*(360/pow(2,16))

    def __str__(self):
        return (
            f'Item200: Calculated Track Velocity in Polar Co-ordinates\n'
            f' Calculated Groundspeed: {self.ground_speed}\n'
            f' Calculated Heading: {self.heading}\n')


######################################################
@dataclass
class Item210:
    sigma_x: int
    sigma_y: int
    sigma_v: int
    sigma_h: int
    
    def __init__(self):
        self.exist    = False
        self.len      = 4
        self.hex      = 0
        self.sigma_x  = 0
        self.sigma_y  = 0
        self.sigma_v  = 0
        self.sigma_h  = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.sigma_x = int(res[:8], 2)*(1/128)
        self.sigma_y = int(res[8:16], 2)*(1/128)
        self.sigma_v = int(res[16:24], 2)*pow(2,-14)
        self.sigma_h = int(res[24:], 2)*(360/pow(2,12))

    def __str__(self):
        return (
            f'Item210: Track Quality\n'
            f' Sigma X: {self.sigma_x}\n'
            f' Sigma Y: {self.sigma_y}\n'
            f' Sigma V: {self.sigma_v}\n'
            f' Sigma H: {self.sigma_h}\n')


######################################################
@dataclass
class Item220:
    aircraft_addr: int
    
    def __init__(self):
        self.exist         = False
        self.len           = 3
        self.hex           = 0
        self.aircraft_addr = 0
      
    def add_info(self, info):
        self.hex = info
        self.aircraft_addr = info
        
    def __str__(self):
        return (
            f'Item220: Aircraft Address\n'
            f' Aircraft Address: {self.aircraft_addr}\n')  
    
    
######################################################
@dataclass
class Item230:
    com: int
    stat: int
    si: int
    mssc: int
    arc: int
    aic: int
    b1a: int
    b1b: int
    
    def __init__(self):
        self.exist = False
        self.len   = 2
        self.hex   = 0
        self.com   = 0
        self.stat  = 0
        self.si    = 0
        self.mssc  = 0
        self.arc   = 0
        self.aic   = 0
        self.b1a   = 0
        self.b1b   = 0
    
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.com   = int(res[:3], 2)
        self.stat  = int(res[3:6], 2)
        self.si    = int(res[6:7], 2)
        self.mssc  = res[8:9]
        self.arc   = res[9:10]
        self.aic   = res[10:11]
        self.b1a   = res[11:12]
        self.b1b   = res[12:]
        
    def __str__(self):
        return (
            f'Item230: Communications/ACAS Capability and Flight Status\n' 
            f' Communications Cap. of transponder (COM): {self.com}\n' 
            f' Flight Status (STAT): {self.stat}\n'
            f' SI/II Transponde Cap. (SI): {self.si}\n'
            f' Mode-S Specific Service Cap. (MSSC): {self.mssc}\n'
            f' Altitud Reporting Cap. (ARC): {self.arc}\n'
            f' Aircraft ID Cap. (AIC): {self.aic}\n'
            f' BDS 1,0 bit 16 (B1A): {self.b1a}\n'
            f' BDS 1,0 bit 37/40 (B1B): {self.b1b}\n')
    
        
######################################################
@dataclass
class Item240:
    aircraft_id: str
    
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
        self.aircraft_id = ""
        
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
            self.aircraft_id += char_map[aux_map]
            count_bits += char_len
            i += 1  

    def __str__(self):
        return (
            f'Item240: Aircraft Identification\n'
            f' Target Identification: {self.aircraft_id}\n')

            
######################################################
# REVISAR si los bloques se añaden bien y quitar los "self" como parametro 
# de las llamadas a self.add_info(self, info, count_octets)
@dataclass
class Item250:
    #rep: int
    blocks: []
    
    @dataclass
    class BDS:
        bdsdatahex: int
        #bdsdata: classmodes.ModeS()
        bds_type: int
        bdsdata: None
        
        def __init__(self, item090):
            self.exist      = False
            self.len        = 8
            self.bdsdatahex = 0
            self.bds_type   = 0
            self.bdsdata    = classmodes.ModeS()
            self.altitude   = item090.fl*100
        
        def add_info (self, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)
            self.altitude = 0
            self.exist = True
            self.bdsdatahex = info_item[:-2]
            bds1 = int(res[56:60],2)
            bds2 = int(res[60:],2)
            self.bds_type = "BDS{}{}".format(bds1, bds2)
            self.bdsdata.add_info(self.bdsdatahex, self.bds_type)
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            return (
                f' BDS Reg. Data: {self.bds_type}\n'
                f' {self.bdsdata}')
     
    
    def __init__(self, item090):
        self.exist   = False
        self.len     = 0
        self.hex     = 0
        self.rep     = 0
        self.item090 = item090
        self.blocks  = []
        
        
    def add_info(self, info = str, count_octets = int):
        aux_count_octets = count_octets
        lenght = 1
        info_item = info[count_octets*2:count_octets*2+lenght*2]
        self.rep = int(info_item, 16)
        count_octets += lenght 
        
        for i in range(self.rep): 
            new_block = self.BDS(self.item090)
            self.blocks.append(new_block)
            count_octets = self.blocks[i].add_info(info, count_octets)
        
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets

    def __str__(self):
        str_bds = 'Item250: BDS Register Data\n'
        if self.exist:
           for i in range(self.rep):
               str_bds +=  f' Block {i}:\n {self.blocks[i]}\n'
        return str_bds


######################################################
@dataclass
class Item260:
    acasra: int
    
    def __init__(self):
        self.exist  = False
        self.len    = 7
        self.hex    = 0
        self.acasra = 0
      
    def add_info(self, info):
        self.hex = info
        self.acasra = hexabin(info, 16)
        
    def __str__(self):
        return (
            f'Item260: Resolution Advisory Report\n'
            f' Current active ACAS RA: {self.acasra}\n')  


#################################################
###  Reserved Expansion Field implementation  ###
#################################################

@dataclass
class SUM:
    m5: int
    idd: int
    da: int
    m1: int
    m2: int
    m3: int
    mc: int
    
    def __init__(self):
        self.exist  = False
        self.len    = 1
        self.m5     = 0
        self.idd    = 0
        self.da     = 0
        self.m1     = 0
        self.m2     = 0
        self.m3     = 0
        self.mc     = 0
            
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = hexabin(info_item, 16)
        self.exist = True
        self.m5    = res[:1]
        self.idd    = res[1:2]
        self.da    = res[2:3]
        self.m1    = res[3:4]
        self.m2    = res[4:5]
        self.m3    = res[5:6]
        self.mc    = res[6:7]
        count_octets += self.len        
        return count_octets
    
    def __str__(self):
        if self.exist:
            return (
                ' Mode 5 Summary:\n'
                f'  M5: {self.m5}\n'
                f'  ID: {self.idd}\n'
                f'  DA: {self.da}\n'
                f'  M1: {self.m1}\n'
                f'  M2: {self.m2}\n'
                f'  M3: {self.m3}\n'
                f'  MC: {self.mc}\n\n')
        return ""

@dataclass
class PMN:
    pin: int
    nav: int
    nat: int
    mis: int

    def __init__(self):
        self.exist = False
        self.len   = 4
        self.pin   = 0
        self.nav   = 0
        self.nat   = 0
        self.mis   = 0
            
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = hexabin(info_item, 16)        
        self.exist = True
        self.pin   = res[2:16]
        self.nav   = res[18:19]
        self.nat   = res[19:24]
        self.mis   = res[26:]
        count_octets += self.len
        return count_octets

    def __str__(self):
        if self.exist:
            return (
                ' Mode 5 PIN / National Origin / Mission Code:\n'
                f'  PIN: {self.pin}\n'
                f'  NAV: {self.nav}\n'
                f'  NAT: {self.nat}\n'
                f'  MIS: {self.mis}\n\n')
        return ""        
    
@dataclass    
class PMNO:
    pin: int
    nov: int
    no: int
    
    def __init__(self):
        self.exist = False
        self.len   = 4
        self.pin   = 0
        self.nov   = 0
        self.no    = 0
            
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = hexabin(info_item, 16)        
        self.exist = True
        self.pin   = res[2:16]
        self.nov   = res[20:21]
        self.no    = res[21:]
        count_octets += self.len        
        return count_octets

    def __str__(self):
        if self.exist:
            return (
                ' Mode 5 PIN / National Origin:\n'
                f'  PIN: {self.pin}\n'
                f'  NOV: {self.nov}\n'
                f'  NO:  {self.no}\n\n')
        return ""   

@dataclass
class POS:
    latitude: int
    longitude: int

    def __init__(self):
        self.exist     = False
        self.len       = 6
        self.latitude  = 0
        self.longitude = 0
            
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = hexabin(info_item, 16)        
        self.exist = True
        self.latitude  = twos_comp(int(res[:24], 2), len(res[:24]))*(180/pow(2,23)) 
        self.longitude = twos_comp(int(res[24:], 2), len(res[24:]))*(180/pow(2,23))
        count_octets += self.len        
        return count_octets
    
    def __str__(self):
        if self.exist:
            return (
                ' Mode 5 Reported Position:\n'
                f' Latitude: {self.latitude}\n'
                f' Longitude: {self.longitude}\n\n')
        return ""

@dataclass
class GA:
    res: int
    ga: int

    def __init__(self):
        self.exist = False
        self.len   = 2
        self.res   = 0
        self.ga    = 0
            
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = hexabin(info_item, 16)        
        self.exist = True
        self.res = res[1:2]
        if self.res == '0':
            self.ga = twos_comp(int(res[2:], 2), len(res[2:]))*25*100
        if self.res == '1':
            self.ga = twos_comp(int(res[2:], 2), len(res[2:]))*25*25
        count_octets += self.len        
        return count_octets
    
    def __str__(self):
        if self.exist:
            return (
                ' Mode 5 GNSS-derived Altitude:\n'
                f'  RES: {self.res}\n'
                f'  GA:  {self.ga}\n\n')
        return ""
    
@dataclass    
class EM1:
    v: int
    g: int
    l: int
    em1: int

    def __init__(self):
        self.exist = False
        self.len   = 2
        self.v     = 0
        self.g     = 0
        self.l     = 0
        self.em1   = 0
            
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = hexabin(info_item, 16)        
        self.exist = True
        self.v = res[:1]
        self.g = res[1:2]
        self.l = res[2:3]
        # Convert str bin to int, then to octal
        aux = oct(int(res[4:], 2))
        # Get rid from the initial "0o"
        self.em1 = aux[2:]
        count_octets += self.len        
        return count_octets        
    
    def __str__(self):
        if self.exist:
            return (
                ' Extended Mode 1 Code in Octal Representation\n'
                f' V: {self.v} | G: {self.g} | L: {self.l}\n'
                f' Extended Mode 1 code: {self.em1}\n\n')
        return ""        
    
@dataclass    
class TOS:
    tos: int

    def __init__(self):
        self.exist = False
        self.len   = 1
        self.tos   = 0
            
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = hexabin(info_item, 16)        
        self.exist = True
        self.tos = twos_comp(int(res, 2), len(res))*(1/128)
        count_octets += self.len        
        return count_octets  
    
    def __str__(self):
        if self.exist:
            return (
                ' Time Offset for POS and GA:\n'
                f'  TOS: {self.tos}\n\n')
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
                ' X Pulse Presence:\n'
                f'  XP:   {self.xp}\n'
                f'  X5:   {self.x5}\n'
                f'  XC:   {self.xc}\n'
                f'  X3:   {self.x3}\n'
                f'  X2:   {self.x2}\n'
                f'  X1:   {self.x1}\n\n')
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
        self.fom = res[3:]
        count_octets += self.len        
        return count_octets  
    
    def __str__(self):
        if self.exist:
            return (
                ' Figure of Merit:\n'
                f'  FOM:  {self.fom}\n\n')
        return ""
 
    
######################################################
@dataclass     
class MD5:
    summ: SUM()
    pmn: PMN()
    pos: POS()
    ga: GA()
    em1: EM1()
    tos: TOS()
    xp: XP()
    
    def __init__(self):
        self.exist  = False
        self.len    = 1 
        self.octet  = 0
        self.summ   = SUM()
        self.pmn    = PMN()
        self.pos    = POS()
        self.ga     = GA()
        self.em1    = EM1()
        self.tos    = TOS()
        self.xp     = XP()
        self.fx     = 0
    
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
            count_octets = self.pnm.add_info(self, info, count_octets)
        if self.octet[2] == '1':
            count_octets = self.pos.add_info(self, info, count_octets)
        if self.octet[3] == '1':
            count_octets = self.ga.add_info(self, info, count_octets)
        if self.octet[4] == '1':
            count_octets = self.em1.add_info(self, info, count_octets)
        if self.octet[5] == '1':
            count_octets = self.tos.add_info(self, info, count_octets)
        if self.octet[6] == '1':
            count_octets = self.xp.add_info(self, info, count_octets)
                    
        return count_octets
    
    def __str__(self):
        if self.exist:
            return (
                ' MD5 - Mode 5 Reports:\n'
                f'{self.summ}{self.pno}{self.em1}'
                f'{self.cp}{self.fom}{self.m2}\n\n')
        return ""  
    
     
######################################################
@dataclass        
class M5N:
    octet_1: 'M5N.Octet1()'
    octet_2: 'M5N.Octet2()'
    
    @dataclass
    class Octet2:
        octet: int
        fom: FOM()
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.octet = 0
            self.fom   = FOM()
            self.fx    = 0
        
        def add_info (self, item, info = str, count_octets = int):
            if self.octet[0] == '1':
                count_octets = self.fom.add_info(self, info, count_octets)
            if self.octet[7]:
                self.fx = self.octet[7]
            return count_octets
        
        def __str__(self, item):
            if self.exist:
                return (
                    f' FOM:  {self.fom}\n\n')
            return "" 
      
    @dataclass    
    class Octet1:
        summ: SUM()
        pmno: PMNO()
        pos: POS()
        ga: GA()
        em1: EM1()
        tos: TOS()
        xp: XP()
        
        def __init__(self):
            self.exist  = False
            self.len    = 1 
            self.octet  = 0
            self.summ   = SUM()
            self.pmno   = PMNO()
            self.pos    = POS()
            self.ga     = GA()
            self.em1    = EM1()
            self.tos    = TOS()
            self.xp     = XP()
            self.fx     = 0
        
        def add_info (self, item, info = str, count_octets = int):
            if self.octet[0] == '1':
                count_octets = self.sum.add_info(self, info, count_octets)
            if self.octet[1] == '1':
                count_octets = self.pmn.add_info(self, info, count_octets)
            if self.octet[2] == '1':
                count_octets = self.pos.add_info(self, info, count_octets)
            if self.octet[3] == '1':
                count_octets = self.ga.add_info(self, info, count_octets)
            if self.octet[4] == '1':
                count_octets = self.em1.add_info(self, info, count_octets)
            if self.octet[5] == '1':
                count_octets = self.tos.add_info(self, info, count_octets)
            if self.octet[6] == '1':
                count_octets = self.xp.add_info(self, info, count_octets)
            if self.octet[7]:
                self.fx = self.octet[7]
            return count_octets
   
        def __str__(self, item):
            return (
                ' M5N - Mode 5 Reports, New Format:\n\n'
                f' SUM: {self.sum}\n PMN: {self.pnm}\n POS: {self.pos}\n'
                f' GA:  {self.ga}\n EM1:  {self.em1}\n TOS: {self.tos}\n' 
                f' XP:  {self.xp}\n' + item.octet_2.__str__(item))      
   
    def __init__(self):
        self.exist   = False
        self.len     = 0
        self.hex     = 0
        self.octet_1 = self.Octet1()
        self.octet_2 = self.Octet2()
        self.fx      = 0   # There is no more documentacion about this FX
        

        
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
            self.fx  = res[7:]
        
        if self.octet_1.exist:
            count_octets = self.octet_1.add_info(self, info, count_octets)
        
            if self.octet_2.exist:
                count_octets = self.octet_2.add_info(self, info, count_octets)
        
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets
        
    
    def __str__(self):
        return self.octet_1.__str__(self)


######################################################
@dataclass
class M4E:
    foe_fri: int

    def __init__(self):
        self.exist   = False
        self.len     = 1
        self.foe_fri = 0
        self.fx      = 0  # There is no more documentacion about this FX

    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = hexabin(info_item, 16)
        self.exist = True 
        self.foe_fri = res[5:7]
        self.fx = res[7:]
        count_octets += self.len            
        return count_octets
        
    def __str__(self):
        if self.exist:
            return (
                ' M4E - Extended Mode 4 Report:\n'
                f' FOE/FRI:  {self.foe_fri}\n\n')
        return "" 


######################################################
@dataclass
class RPC:
    sco: 'RPC.SCO()'
    scr: 'RPC.SCR()'
    ar: 'RPC.AR()'
    rw: 'RPC.RW()'
    
    @dataclass        
    class SCO:
        sco: int
    
        def __init__(self):
            self.exist = False
            self.len   = 1
            self.sco   = 0
                
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)
            self.exist = True
            self.sco   = int(res, 2)
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    ' Score:\n'
                    f'  Score:  {self.score}\n\n')
            return ""
    
    @dataclass
    class SCR:
        scr: int
    
        def __init__(self):
            self.exist = False
            self.len   = 2
            self.scr   = 0
                
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)            
            self.exist = True
            self.scr   = int(res, 2)*0.1
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    ' Signal / Clutter Radio:\n'
                    f'  SCR: {self.scr}\n\n')
            return ""
       
    @dataclass    
    class AR:
        ar: int
    
        def __init__(self):
            self.exist = False
            self.len   = 2
            self.ar    = 0
                
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)            
            self.exist = True
            self.ar    = int(res, 2)*(1/256)
            count_octets += self.len            
            return count_octets  
        
        def __str__(self):
            if self.exist:
                return (
                    ' Ambiguous Range:\n'
                    f'  AR   {self.ar}\n\n')
            return ""
        
    @dataclass   
    class RW:
        rw: int
        
        def __init__(self):
            self.exist = False
            self.len   = 2
            self.rw    = 0
                
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)            
            self.exist = True
            self.rw    = int(res, 2)*(1/256)
            count_octets += self.len            
            return count_octets 
        
        def __str__(self):
            if self.exist:
                return (
                    ' Range Width:\n'
                    f'  RW: {self.rw}\n\n')
            return ""        
        
        
    def __init__(self):
        self.exist = False
        self.len   = 1 
        self.octet = 0
        self.sco   = self.SCO()
        self.scr   = self.SCR()
        self.ar    = self.AR()
        self.rw    = self.RW()
        self.fx    = 0
    
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = "{0:08b}".format(int(info_item, 16))
        self.exist = True
        self.octet = res
        self.fx = res[-1]
        count_octets += self.len
        if self.octet[0] == '1':
            count_octets = self.sco.add_info(self, info, count_octets)
        if self.octet[1] == '1':
            count_octets = self.scr.add_info(self, info, count_octets)
        if self.octet[2] == '1':
            count_octets = self.rw.add_info(self, info, count_octets)
        if self.octet[3] == '1':
            count_octets = self.ar.add_info(self, info, count_octets)
                    
        return count_octets
    
    def __str__(self):
        if self.exist:
            return (
                ' Radar Plot Characteristics\n'
                f'{self.sco}{self.scr}{self.rw}'
                f'{self.ar}\n\n')
        return ""


######################################################
@dataclass
class ERR:
    rho: int
    
    def __init__(self):
        self.exist = False
        self.len   = 3
        self.rho   = 0
            
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = hexabin(info_item, 16)
        self.exist = True 
        self.rho = int(res, 2)*(1/256)
        count_octets += self.len        
        return count_octets
    
    def __str__(self):
        if self.exist:
            return (
                ' Extended Range Report:\n'
                f' RHO: {self.rho}\n\n')
        return "" 


######################################################
@dataclass
class PTL:
    scn: int
    rc: int
    ac: int
    ssr: int
    psr: int
    plotnr: int

    def __init__(self):
        self.exist  = False
        self.len    = 3
        self.scn    = 0
        self.rc     = 0
        self.ac     = 0
        self.ssr    = 0
        self.psr    = 0
        self.plotnr = 0

            
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = hexabin(info_item, 16)        
        self.exist  = True
        self.scn    = res[3:4]
        self.rc     = res[4:5]
        self.ac     = res[5:6]
        self.ssr    = res[6:7]
        self.psr    = res[7:8]
        self.plotnr = res[8:]
        count_octets += self.len        
        return count_octets  
    
    def __str__(self):
        if self.exist:
            return (
                ' Plot/Track Link:\n'
                f'  SCN:    {self.scn}\n'
                f'  RC:     {self.rc}\n'
                f'  AC:     {self.ac}\n'
                f'  SSR:    {self.ssr}\n'
                f'  PSR:    {self.psr}\n'
                f'  PLOTNR: {self.plotnr}\n\n')
        return ""


@dataclass
class ATL:
    blocks: []

    @dataclass
    class ADSBTL:
        adsbrepnr: int
        
        def __init__(self):
            self.exist     = False
            self.len       = 2
            self.adsbrepnr = 0
        
        def add_info (self, info = str, count_octets = int):
            #info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info, 16)
            self.exist = True
            self.adsbrepnr = res
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            return (
                f' Ref. to ADS-B Report: {self.adsbrepnr}\n')
     
    
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
            new_block = self.ADSBTL()
            self.blocks.append(new_block)
            count_octets = self.blocks[i].add_info(info, count_octets)
        
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets

    def __str__(self):
        str_bds = ' ADS-B/Track Link:\n'
        if self.exist:
           for i in range(self.rep):
               str_bds +=  f' Block {i}:\n {self.blocks[i]}\n'
        return str_bds
    
    
@dataclass
class TRN:
    probaturn: int
    
    def __init__(self):
        self.exist      = False
        self.len        = 1
        self.probaturn  = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.probaturn = int(res, 2)*0.01
        
    def __str__(self):
        return (
            f' Turn State:\n'
            f'  Probability of Circular Model: {self.probaturn}\n')


@dataclass
class NPP:
    predrho: int
    predtheta: int
    evolrhostart: int
    evolrhoend: int
    evolthetastart: int
    evolthetaend: int
    noiserhostart: int
    noiserhoend: int
    noisethetastart: int
    noisethetaend: int
    predtime: int

    def __init__(self):
        self.exist           = False
        self.len             = 22
        self.predrho         = 0
        self.predtheta       = 0
        self.evolrhostart    = 0
        self.evolrhoend      = 0
        self.evolthetastart  = 0
        self.evolthetaend    = 0
        self.noiserhostart   = 0
        self.noiserhoend     = 0
        self.noisethetastart = 0
        self.noisethetaend   = 0
        self.predtime        = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.predrho         = int(res[:16], 2)*(1/128)
        self.predtheta       = int(res[16:32], 2)*(360/pow(2,16))
        self.evolrhostart    = int(res[32:48], 2)*(1/128)
        self.evolrhoend      = int(res[48:64], 2)*(1/128)
        self.evolthetastart  = int(res[64:80], 2)*(360/pow(2,16))
        self.evolthetaend    = int(res[80:96], 2)*(360/pow(2,16))
        self.noiserhostart   = int(res[96:112], 2)*(1/128)
        self.noiserhoend     = int(res[112:128], 2)*(1/128)
        self.noisethetastart = int(res[128:144], 2)*(360/pow(2,16))
        self.noisethetaend   = int(res[144:160], 2)*(360/pow(2,16))
        self.predtime        = int(res[160:], 2)*(1/128)
        #self.probaturn = int(res, 2)*0.01
        
    def __str__(self):
        return (
            f' Next Predicted Position:\n'
            f'  Predicted Range: {self.predrho}\n'
            f'  Predicted Azimuth: {self.predtheta}\n'
            f'  Predicted Closest Range: {self.evolrhostart}\n'
            f'  Predicted Largest Range: {self.evolrhoend}\n'
            f'  Predicted Smallest Azimuth: {self.evolthetastart}\n'
            f'  Predicted Largest Azimuth: {self.evolthetaend}\n'
            f'  Predicted Closest Range: {self.noiserhostart}\n'
            f'  Predicted Largest Range: {self.noiserhoend}\n'
            f'  Predicted Smallest Azimuth: {self.noisethetastart}\n'
            f'  Predicted Largest Azimuth: {self.noisethetaend}\n'
            f'  Predicted Detection Time: {self.predtime}\n\n'
            )


@dataclass
class DLK:
    blocks: []
    
    @dataclass
    class DLC:
        origin: int
        state: int
        
        def __init__(self):
            self.exist  = False
            self.len    = 1
            self.type   = 0
            self.origin = 0
            self.state  = 0
        
        def add_info (self, info = str, count_octets = int):
            #info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info, 16)
            self.exist = True
            self.type   = int(res[:4], 2)
            self.origin = int(res[4:6], 2)
            self.state  = int(res[6:], 2)
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            return (
                f'  Type of Message Protocol: {self.type}\n'
                f'  Frame Detection: {self.origin}\n'
                f'  Frame State: {self.state}\n\n')
     
    
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
            new_block = self.DLC()
            self.blocks.append(new_block)
            count_octets = self.blocks[i].add_info(info, count_octets)
        
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets

    def __str__(self):
        str_bds = ' Data Link Characteristics\n'
        if self.exist:
           for i in range(self.rep):
               str_bds +=  f' Block {i}:\n {self.blocks[i]}\n'
        return str_bds


@dataclass
class LCK:
    ls: int
    loctim: int

    def __init__(self):
        self.exist   = False
        self.len     = 2
        self.ls      = 0
        self.loctim  = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.ls      = res[:1]
        self.loctim  = int(res[1:], 2)*1
        
    def __str__(self):
        return (
            f' Lockout Characteristics:\n'
            f'  Lockout State: {self.ls}\n'
            f'  Lockout Time: {self.loctim}\n\n')
    
    
@dataclass
class TC:
    tcount1: int
    tcode1: int
    tcount2:int
    tcode2: int
    tcount3: int
    tcode3: int

    def __init__(self):
        self.exist   = False
        self.len     = 6
        self.tcount1 = 0
        self.tcode1  = 0
        self.tcount2 = 0
        self.tcode2  = 0
        self.tcount3 = 0
        self.tcode3  = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)        
        self.tcount1 = int(res[7:11],2)
        self.tcode1  = res[11:16]
        self.tcount2 = int(res[16:20],2)
        self.tcode2  = res[20:32]
        self.tcount3 = int(res[32:36],2)
        self.tcode3  = res[36:]
        
    def __str__(self):
        return (
            f' Transition Codes:\n'
            f'  TCOUNT Mode 1: {self.tcount1}\n'
            f'  TCODE Mode 1: {self.tcode1}\n'
            f'  TCOUNT Mode 2: {self.tcount2}\n'
            f'  TCODE Mode 2: {self.tcode2}\n'
            f'  TCOUNT Mode 3: {self.tcount3}\n'
            f'  TCODE Mode 1: {self.tcode3}\n\n')
    
    
@dataclass
class TLC:
    acqi: int
    trkupdctr: int
    lasttrkupd: int

    def __init__(self):
        self.exist      = False
        self.len        = 4
        self.acqi       = 0
        self.trkupdctr  = 0
        self.lasttrkupd = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.acqi = int(res[:2],2)
        self.trkupdctr  = int(res[2:16],2)
        self.lasttrkupd = int(res[16:],2)*1
        
    def __str__(self):
        return (
            f' Track Lifecycle:\n'
            f'  Acquisition Status Indicator: {self.acqi}\n'
            f'  Track Update Counter: {self.trkupdctr}\n'
            f'  Time since last Track Update: {self.lasttrkupd}\n\n'
            )
    

@dataclass
class ASI:
    blocks: []
    
    @dataclass
    class ASIBlock:
        sacadjs: int
        sicadjs: int
        time_of_day_scn: int
        datause: int
        drna: int
        drn: int
        
        def __init__(self):
            self.exist           = False
            self.len             = 8
            self.sacadjs         = 0
            self.sicadjs         = 0
            self.time_of_day_scn = 0
            self.datause         = 0
            self.drna            = 0
            self.drn             = 0
        
        def add_info (self, info = str, count_octets = int):
            #info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info, 16)
            self.exist = True
            self.sacadjs         = int(res[:8], 2)
            self.sicadjs         = int(res[8:16], 2)
            self.time_of_day_scn = int(res[16:40], 2)
            self.datause         = int(res[40:47], 2)
            self.drna            = int(res[47:48], 2)
            self.drn             = int(res[48:], 2)
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            return (
                f'  SAC of the Adjacent Sensor: {self.sacadjs}\n'
                f'  SIC of the Adjacent Sensor: {self.sicadjs}\n'
                f'  Absolute Timestamp in UTC (SCN): {self.time_of_day_scn}\n'
                f'  Use of Adjacent Sensor Data: {self.datause}\n'
                f'  DRN Availability: {self.drna}\n'
                f'  Duplicate Address Ref.: {self.drn}\n\n')
     
    
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
            new_block = self.ASIBlock()
            self.blocks.append(new_block)
            count_octets = self.blocks[i].add_info(info, count_octets)
        
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets

    def __str__(self):
        str_bds = ' Adjacent Sensor Information:\n'
        if self.exist:
           for i in range(self.rep):
               str_bds +=  f' Block {i}:\n {self.blocks[i]}\n'
        return str_bds


@dataclass
class TES:
    tes: int

    def __init__(self):
        self.exist = False
        self.len   = 1
        self.tes   = 0
        
    def add_info(self, info):
        self.hex = info
        #res = "{0:08b}".format(int(info[:5], 16))
        #res = res + "{0:08b}".format(int(info[5:], 16))
        res = hexabin(info, 16)
        self.tes = int(res, 2)
        
    def __str__(self):
        return (
            f' Track Extrapolation Source:\n'
            f'  Track Extrapolation Source: {self.tes}\n\n')
    
    
@dataclass
class IR:
    ir: int
    m3a: int

    def __init__(self):
        self.exist = False
        self.len   = 1
        self.ir    = 0
        self.m3a   = 0
        
    def add_info(self, info):
        self.hex = info
        res = hexabin(info, 16)
        self.ir  = res[:1]
        self.m3a = int(res[1:], 2)*1
        
    def __str__(self):
        return (
            f' Identity Requested\n'
            f'  Identity Requested latest scan: {self.ir}\n'
            f'  Age of Mode 3/A Code: {self.m3a}\n\n')
    

@dataclass
class RTC:
    octet_1: 'RTC.Octet1()'
    octet_2: 'RTC.Octet2()'
    
    @dataclass
    class Octet2:
        tlc: TLC()
        asi: ASI()
        tes: TES()
        ir: IR()
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.octet = 0
            self.tlc   = TLC()
            self.asi   = ASI()
            self.tes   = TES()
            self.ir    = IR()
            self.fx    = 0
        
        def add_info (self, item, info = str, count_octets = int):
            if self.octet[0] == '1':
                count_octets = self.fom.add_info(self, info, count_octets)
            if self.octet[7]:
                self.fx = self.octet[7]
            return count_octets
        
        def __str__(self, item):
            if self.exist:
                return (
                    f' TLC: {self.tlc}\n ASI: {self.asi}\n TES: {self.tes}\n'
                    f' IR:  {self.ir}\n\n')
            return "" 
    
    @dataclass        
    class Octet1:
        ptl: PTL()
        atl: ATL()
        trn: TRN()
        npp: NPP()
        dlk: DLK()
        lck: LCK()
        tc: TC()
        
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.octet = 0
            self.ptl   = PTL()
            self.atl   = ATL()
            self.trn   = TRN()
            self.npp   = NPP()
            self.dlk   = DLK()
            self.lck   = LCK()
            self.tc    = TC()
            self.fx    = 0
        
        def add_info (self, item, info = str, count_octets = int):
            if self.octet[0] == '1':
                count_octets = self.sum.add_info(self, info, count_octets)
            if self.octet[1] == '1':
                count_octets = self.pmn.add_info(self, info, count_octets)
            if self.octet[2] == '1':
                count_octets = self.pos.add_info(self, info, count_octets)
            if self.octet[3] == '1':
                count_octets = self.ga.add_info(self, info, count_octets)
            if self.octet[4] == '1':
                count_octets = self.em1.add_info(self, info, count_octets)
            if self.octet[5] == '1':
                count_octets = self.tos.add_info(self, info, count_octets)
            if self.octet[6] == '1':
                count_octets = self.xp.add_info(self, info, count_octets)
            if self.octet[7]:
                self.fx = self.octet[7]
            return count_octets
   
        def __str__(self, item):
            return (
                ' Radar Track Characteristics:\n'
                f' PTL: {self.ptl}\n ATL: {self.atl}\n TRN: {self.trn}\n'
                f' NPP: {self.npp}\n DLK: {self.dlk}\n LCK: {self.lck}\n' 
                f' TC:  {self.tc}\n' + item.octet_2.__str__(item))      
   
    
    def __init__(self):
        self.exist   = False
        self.len     = 0
        self.hex     = 0
        self.octet_1 = self.Octet1()
        self.octet_2 = self.Octet2()
        self.fx      = 0   # There is no more documentacion about this FX


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
            self.fx  = res[7:]
        
        if self.octet_1.exist:
            count_octets = self.octet_1.add_info(self, info, count_octets)
        
            if self.octet_2.exist:
                count_octets = self.octet_2.add_info(self, info, count_octets)
        
        self.hex = info[aux_count_octets*2:count_octets*2]
        return count_octets
        
    
    def __str__(self):
        return self.octet_1.__str__(self)


######################################################
@dataclass
class CPC:
    pnb: 'CPC.PNB()'
    rpl: 'CPC.RPL()'
    snb: 'CPC.SNB()'
    date: 'CPC.DATE()'
    
    @dataclass
    class PNB:
        plotnbr: int
    
        def __init__(self):
            self.exist   = False
            self.len     = 2
            self.plotnbr = 0
                
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)
            self.exist = True
            self.plotnbr = res
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    ' Plot Number:\n'
                    f'  Unique ID of Plot Record: {self.plotnbr}\n\n')
            return ""
    
    @dataclass
    class RPL:
        #rep: int
        blocks: []
        
        @dataclass
        class RPLBlock:
            typeb: int
            replynbr: int
            
            def __init__(self):
                self.exist    = False
                self.len      = 3
                self.typeb     = 0
                self.replynbr = 0
            
            def add_info (self, info = str, count_octets = int):
                #info_item = info[count_octets*2:count_octets*2+self.len*2]
                res = hexabin(info, 16)
                self.exist = True
                self.typeb  = int(res[:8], 2)
                self.replynbr = res[8:]
                count_octets += self.len
                return count_octets
            
            def __str__(self):
                return (
                    f'  Reply Type: {self.typeb}\n'
                    f'  Unique ref. to plot record: {self.replynbr}\n\n')
     
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
                new_block = self.RPLBlock()
                self.blocks.append(new_block)
                count_octets = self.blocks[i].add_info(info, count_octets)
            self.hex = info[aux_count_octets*2:count_octets*2]
            return count_octets
    
        def __str__(self):
            str_bds = ' Replies / Plot Link\n'
            if self.exist:
               for i in range(self.rep):
                   str_bds +=  f' Block {i}:\n {self.blocks[i]}\n'
            return str_bds
        
    @dataclass
    class SNB:
        scannbr: int
    
        def __init__(self):
            self.exist   = False
            self.len     = 1
            self.scannbr = 0
                
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)
            self.exist = True
            self.scannbr = int(res, 2)
            count_octets += self.len
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    ' Scan Number:\n'
                    f'  Scan Number: {self.scannbr}\n\n')
            return ""
    
    @dataclass
    class DATE:
        date: int
    
        def __init__(self):
            self.exist = False
            self.len   = 4
            self.y1    = 0
            self.y2    = 0
            self.y3    = 0
            self.y4    = 0
            self.m1    = 0
            self.m2    = 0
            self.d1    = 0
            self.d2    = 0
            self.date  = 0
                
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = hexabin(info_item, 16)
            self.exist = True
            self.y1    = int(res[:4],2)
            self.y2    = int(res[4:8],2)
            self.y3    = int(res[8:12],2)
            self.y4    = int(res[12:16],2)
            self.m1    = int(res[16:20],2)
            self.m2    = int(res[20:24],2)
            self.d1    = int(res[20:24],2)
            self.d2    = int(res[20:24],2)
            self.date  = (f'{self.y1}{self.y2}{self.y3}{self.y4}/{self.m1}{self.m2}'
                          f'/{self.d1}{self.d2}')
            count_octets += self.len            
            return count_octets
        
        def __str__(self):
            if self.exist:
                return (
                    ' Date:\n'
                    f'  Date: {self.date}\n\n')
            return ""
    
        
    def __init__(self):
        self.exist = False
        self.len   = 1 
        self.octet = 0
        self.pnb   = self.PNB()
        self.rpl   = self.RPL()
        self.snb   = self.SNB()
        self.date  = self.DATE()
        self.fx    = 0
    
    def add_info (self, item, info = str, count_octets = int):
        info_item = info[count_octets*2:count_octets*2+self.len*2]
        res = "{0:08b}".format(int(info_item, 16))
        self.exist = True
        self.octet = res
        self.fx = res[-1]
        count_octets += self.len
        
        if self.octet[0] == '1':
            count_octets = self.pnb.add_info(self, info, count_octets)
        if self.octet[1] == '1':
            count_octets = self.rpl.add_info(self, info, count_octets)
        if self.octet[2] == '1':
            count_octets = self.snb.add_info(self, info, count_octets)
        if self.octet[3] == '1':
            count_octets = self.date.add_info(self, info, count_octets)
                    
        return count_octets
    
    def __str__(self):
        if self.exist:
            return (
                ' Common and Plot Characteristics\n'
                f'{self.pnb}{self.rpl}{self.snb}'
                f'{self.date}\n\n')
        return ""


######################################################
@dataclass
class RE:
    #len_indicator: int
    data: 'RE.Data()'
    
    @dataclass
    class Data:
        octet: int
        md5: MD5()
        m5n: M5N()
        m4e: M4E()
        rpc: RPC()
        err: ERR()
        rtc: RTC()
        cpc: CPC()
    
        def __init__(self):
            self.exist = False
            self.len   = 1 
            self.octet = 0
            self.md5   = MD5()
            self.m5n   = M5N()
            self.m4e   = M4E()
            self.rpc   = RPC()
            self.err   = ERR()
            self.rtc   = RTC()
            self.cpc   = CPC()
        
        def add_info (self, item, info = str, count_octets = int):
            info_item = info[count_octets*2:count_octets*2+self.len*2]
            res = "{0:08b}".format(int(info_item, 16))
            self.exist = True
            self.octet = res
            count_octets += self.len
            
            if self.octet[0] == '1':
                count_octets = self.md5.add_info(self, info, count_octets)
            if self.octet[1] == '1':
                count_octets = self.m5n.add_info(self, info, count_octets)
            if self.octet[2] == '1':
                count_octets = self.m4e.add_info(self, info, count_octets)
            if self.octet[3] == '1':
                count_octets = self.rpc.add_info(self, info, count_octets)
            if self.octet[4] == '1':
                count_octets = self.err.add_info(self, info, count_octets)
            if self.octet[5] == '1':
                count_octets = self.rtc.add_info(self, info, count_octets)
            if self.octet[6] == '1':
                count_octets = self.cpc.add_info(self, info, count_octets)
            
            return count_octets
        
        def __str__(self, item):
            return (
                'RE: Reserved Expansion Field\n'
                f'{self.md5}{self.m5n}{self.m4e}'
                f'{self.rpc}{self.err}{self.rtc}' 
                f'{self.cpc}\n')
   
    
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
class BlockCat48:
    fspec: int
    item010: Item010()
    item140: Item140()
    item020: Item020()
    item040: Item040()
    item070: Item070()
    item090: Item090()
    item130: Item130()
    item220: Item220()
    item240: Item240()
    item250: Item250(0)
    item161: Item161()
    item042: Item042()
    item200: Item200()
    item170: Item170()
    item210: Item210()
    item030: Item030()
    item080: Item080()
    item100: Item100()
    item110: Item110()
    item120: Item120()
    item230: Item230()
    item260: Item260()
    item055: Item055()
    item050: Item050()
    item065: Item065()
    item060: Item060()
    sp     : ItemNotUsed()
    re     : RE()
    
    def __init__(self):
        self.fspec   = 0
        self.item010 = Item010()
        self.item140 = Item140()
        self.item020 = Item020()
        self.item040 = Item040()
        self.item070 = Item070()
        self.item090 = Item090()
        self.item130 = Item130()
        self.item220 = Item220()
        self.item240 = Item240()
        self.item250 = Item250(self.item090)
        self.item161 = Item161()
        self.item042 = Item042()
        self.item200 = Item200()
        self.item170 = Item170()
        self.item210 = Item210()
        self.item030 = Item030()
        self.item080 = Item080()
        self.item100 = Item100()
        self.item110 = Item110()
        self.item120 = Item120()
        self.item230 = Item230()
        self.item260 = Item260()
        self.item055 = Item055()
        self.item050 = Item050()
        self.item065 = Item065()
        self.item060 = Item060()
        self.sp      = ItemNotUsed()
        self.re      = RE()
       
    
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
        new_block = BlockCat48()
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
class Category48:
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
