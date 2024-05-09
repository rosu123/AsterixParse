#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 17:01:30 2024

@author: rodrigo
"""

import math
from dataclasses import dataclass, asdict
import logging


######################################################

def hexabin(num = int, base = int):
  return bin(int(num, base))[2:].zfill(len(num) * int(math.log2(base)))


def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val     


def calculate_static_p(altitude_ft):
    # Constants of the standard atmospheric model
    P0 = 101325     # Standard sea level pressure in Pa
    L = 0.0065      # Rate of temperature variation with altitude in K/m
    T0 = 288.15     # Standard sea level temperature in K
    g = 9.81        # Acceleration due to gravity in m/s²
    R = 287         # Specific gas constant of air in J/(kg·K)

    # Convert altitude from feet to meters
    altitude_meters = altitude_ft * 0.3048

    # Calculate static pressure
    pressure = P0 * (1 - (L * altitude_meters) / T0) ** (g / (R * L))

    return pressure

# Example of use
#aircraft_altitude_ft = 38000  # Altitude (ft)
#mach_aircraft = 0.788         # Mach number

#static_pressure = calculate_static_p(aircraft_altitude_ft)
#print(f"The static pressure at {aircraft_altitude_ft} feet is: {static_pressure:.2f} Pa")


def calculate_cas(altitude_ft, mach_aircraft, static_pressure):
    a0 = 661.47    # Speed of sound at sea level in knots
    P0 = 101325    # Standard sea level pressure in Pa

    q0 = static_pressure*( pow(1+0.2*pow(mach_aircraft,2),7/2) - 1)
    
    cas = a0 * math.sqrt(5 * (pow((q0/P0+1),2/7) -1))

    return cas

#calculated_cas = calculate_cas(aircraft_altitude_ft, mach_aircraft, static_pressure)
#print(f"Calibrated Airspeed (CAS) estimated is: {calculated_cas:.2f} m/s")

    
######################################
@dataclass
class BDS44():
    fom: int
    wind_speed: int
    wind_direction: int
    temperature: int
    avg_static_pressure: int
    turbulence: int
    humidity: int
    
    
    def __init__(self):
        self.exist        = False
        #self.len          = 7
        #self.hex          = 0
        self.fom  = 0
        self.wind_status = 0
        self.wind_speed = 0
        self.wind_direction = 0
        self.temperature = 0
        self.pressure_status = 0
        self.avg_static_pressure = 0
        self.turbulence_status = 0
        self.turbulence = 0
        self.humidity_status = 0
        self.humidity = 0
        
        
    def add_info(self, bds_data: str):
        
        #print("\n---BDS44---")
        res = hexabin(bds_data, 16)
        
        #Figure of merit
        self.fom = res[:4]
        self.fom = int(self.fom, 2)
        #print("fom |{}|".format(self.fom))
        if not (0 <= self.fom < 5):
        #    print("BDS error: fom |{}|".format(self.fom))
            return False
        
        #Wind
        self.wind_status = res[4:5]
        self.wind_status = int(self.wind_status, 2)
        #print("wind_status |{}|".format(self.wind_status))
        if not (self.wind_status == 0 or self.wind_status == 1):
        #    print("BDS error: wind_status |{}|".format(self.wind_status))
            return False
        self.wind_speed = res[5:14]
        self.wind_speed = int(self.wind_speed, 2)*1
        
        self.wind_direction = res[14:23]
        self.wind_direction = int(self.wind_direction, 2)*(180/256)
        
        if self.wind_status == 0 and (self.wind_speed != 0 or self.wind_direction != 0):
        #    print("BDS error: status error\n")
            return False
        if self.wind_status == 1:   
        #    print("wind_speed |{}|".format(self.wind_speed))
            if not (0 <= self.wind_speed <= 511):
        #        print("BDS error: wind_speed |{}|".format(self.wind_speed))
                return False
        #    print("wind_direction |{}|".format(self.wind_direction))
            if not (0 <= self.wind_direction <= 360):
        #        print("BDS error: wind_direction |{}|".format(self.wind_direction))
                return False
        else:
            self.wind_speed = None
            self.wind_direction = None
        
        #Temperature
        self.temperature = res[23:34]
        self.temperature = twos_comp(int(self.temperature, 2), len(self.temperature))*0.25
        #print("temperature |{}|".format(self.temperature))
        if not (-128 <= self.temperature <= 128):
        #    print("BDS error: temperature |{}|".format(self.temperature))
            return False
        
        #Pressure
        self.pressure_status = res[34:35]
        self.pressure_status = int(self.pressure_status, 2)
        #print("pressure_status |{}|".format(self.pressure_status))
        if not (self.pressure_status == 0 or self.pressure_status == 1):
        #    print("BDS error: wind_status |{}|".format(self.pressure_status))
            return False
        self.avg_static_pressure = res[35:46]
        self.avg_static_pressure = int(self.avg_static_pressure, 2)*1
        if self.pressure_status == 0 and self.avg_static_pressure != 0:
        #    print("BDS error: status error\n")
            return False
        if self.pressure_status == 1:
        #    print("avg_static_pressure |{}|".format(self.avg_static_pressure))
            if not (0 <= self.avg_static_pressure <= 2048):
        #        print("BDS error: avg_static_pressure |{}|".format(self.avg_static_pressure))
                return False
        else:
            self.avg_static_pressure = None
        
        #Turbulence
        self.turbulence_status = res[46:47]
        self.turbulence_status = int(self.turbulence_status, 2)
        #print("turbulence_status |{}|".format(self.turbulence_status))
        if not (self.turbulence_status == 0 or self.turbulence_status == 1):
        #    print("BDS error: turbulence_status |{}|".format(self.turbulence_status))
            return False
        self.turbulence = res[47:49]
        self.turbulence = int(self.turbulence, 2)*1
        if self.turbulence_status == 0 and self.turbulence != 0:
        #    print("BDS error: status error\n")
            return False
        if self.turbulence_status == 1:
        #    print("turbulence |{}|".format(self.turbulence))
            if not (0 <= self.turbulence <= 2048):
        #        print("BDS error: turbulence |{}|".format(self.turbulence))
                return False
        else:
            self.turbulence = None
        
        #Turbulence
        self.humidity_status = res[49:50]
        self.humidity_status = int(self.humidity_status, 2)
        #print("humidity_status |{}|".format(self.humidity_status))
        if not (self.humidity_status == 0 or self.humidity_status == 1):
        #    print("BDS error: humidity_status |{}|".format(self.humidity_status))
            return False
        self.humidity = res[50:56]
        self.humidity = int(self.humidity, 2)*(100/64)
        if self.humidity_status == 0 and self.humidity != 0:
        #    print("BDS error: status error\n")
            return False
        if self.humidity_status == 1:
        #    print("humidity |{}|".format(self.humidity))
            if not (0 <= self.humidity <= 100):
        #        print("BDS error: humidity |{}|".format(self.humidity))
                return False
        else:
            self.humidity = None
        
        self.exist = True
        return True
    
    
    def __str__(self):
        if self.exist:
            return (
                f' BDS44: Meteorological routine air report\n'
                f'  Figure of merit / source: {self.fom}\n'
                f'  Status (wind): {self.wind_status}\n'
                f'  Wind speed: {self.wind_speed} kt\n'
                f'  Wind direction: {self.wind_direction} degrees\n'
                f'  Static air temperature: {self.temperature} ºC\n'
                f'  Status (pressure): {self.pressure_status}\n'
                f'  Average static pressure: {self.avg_static_pressure} hPa\n'
                f'  Status (turbulence): {self.turbulence_status}\n'
                f'  Turbulence: {self.turbulence}\n'
                f'  Status (humidity): {self.humidity_status}\n'
                f'  Humidity: {self.humidity} %\n')
        else:
            return""
   
    
#######################################################################  
# DUDA: los limites a la hora de comprobar los valores son distintos al
# rango real del valor
@dataclass
class BDS50:
    roll_angle: int
    true_track_angle: int
    track_angle_rate: int
    ground_speed: int
    true_airspeed: int
    
    
    def __init__(self):
        self.exist        = False
        #self.len          = 7
        #self.hex          = 0
        self.roll_angle_status  = 0
        self.roll_angle = 0
        self.true_track_angle_status = 0
        self.true_track_angle = 0
        self.ground_speed_status = 0
        self.ground_speed = 0
        self.track_angle_rate_status = 0
        self.track_angle_rate = 0
        self.true_airspeed_status = 0
        self.true_airspeed = 0
       
        
    def add_info(self, bds_data: str):
        
        #print("\n---BDS50---")
        res = hexabin(bds_data, 16)
        
        #Roll Angle
        self.roll_angle_status = res[:1]
        self.roll_angle_status = int(self.roll_angle_status, 2)
        #print("roll_angle_status |{}|".format(self.roll_angle_status))
        if not (self.roll_angle_status == 0 or self.roll_angle_status == 1):
        #    print("BDS error: roll_angle_status |{}|".format(self.roll_angle_status))
            return False
        self.roll_angle = res[1:11]
        self.roll_angle = twos_comp(int(self.roll_angle, 2), len(self.roll_angle))*(45/256)
        if self.roll_angle_status == 0 and self.roll_angle != 0:
        #    print("BDS error: status error\n")
            return False
        if self.roll_angle_status == 1:
        #    print("roll_angle |{}|".format(self.roll_angle))
            if not (-90 <= self.roll_angle <= 90):
        #        print("BDS error: roll_angle |{}|".format(self.roll_angle))
                return False
        else:
            self.roll_angle = None
        
        #True Track Angle
        self.true_track_angle_status = res[11:12]
        self.true_track_angle_status = int(self.true_track_angle_status, 2)
        #print("rue_track_angle_status |{}|".format(self.true_track_angle_status))
        if not (self.true_track_angle_status == 0 or self.true_track_angle_status == 1):
        #    print("BDS error: true_track_angle_status |{}|".format(self.true_track_angle_status))
            return False
        self.true_track_angle = res[12:23]
        self.true_track_angle = twos_comp(int(self.true_track_angle, 2), len(self.true_track_angle))*(90/512)
        if self.true_track_angle_status == 0 and self.true_track_angle != 0:
        #    print("BDS error: status error\n")
            return False
        if self.true_track_angle_status == 1:
        #    print("true_track_angle |{}|".format(self.true_track_angle))
            if not (-180 <= self.true_track_angle <= 180):
        #        print("BDS error: true_track_angle |{}|".format(self.true_track_angle))
                return False
        else:
            self.true_track_angle = None
         
        #Ground Speed    
        self.ground_speed_status = res[23:24]
        self.ground_speed_status = int(self.ground_speed_status, 2)
        #print("ground_speed_status |{}|".format(self.ground_speed_status))
        if not (self.ground_speed_status == 0 or self.ground_speed_status == 1):
        #    print("BDS error: ground_speed_status |{}|".format(self.ground_speed_status))
            return False
        self.ground_speed = res[24:34]
        self.ground_speed = int(self.ground_speed, 2)*2
        if self.ground_speed_status == 0 and self.ground_speed != 0:
        #    print("BDS error: status error\n")
            return False
        if self.ground_speed_status == 1:
        #    print("ground_speed |{}|".format(self.ground_speed))
            if not (0 <= self.ground_speed <= 2046):
        #        print("BDS error: ground_speed |{}|".format(self.ground_speed))
                return False
        else:
            self.ground_speed = None
        
        #Track Angle Rate
        self.track_angle_rate_status = res[34:35]
        self.track_angle_rate_status = int(self.track_angle_rate_status, 2)
        #print("track_angle_rate_status |{}|".format(self.track_angle_rate_status))
        if not (self.track_angle_rate_status == 0 or self.track_angle_rate_status == 1):
        #    print("BDS error: track_angle_rate_status |{}|".format(self.track_angle_rate_status))
            return False
        self.track_angle_rate = res[35:45]
        self.track_angle_rate = twos_comp(int(self.track_angle_rate, 2), len(self.track_angle_rate))*(8/256)
        if self.track_angle_rate_status == 0 and self.track_angle_rate != 0:
        #    print("BDS error: status error\n")
            return False
        if self.track_angle_rate_status == 1:
        #    print("roll_angle |{}|".format(self.track_angle_rate))
            if not (-16 <= self.track_angle_rate <= 16):
        #        print("BDS error: roll_angle |{}|".format(self.track_angle_rate))
                return False
        else:
            self.track_angle_rate = None
        
        #True Airspeed
        self.true_airspeed_status = res[45:46]
        self.true_airspeed_status = int(self.true_airspeed_status, 2) 
        #print("true_airspeed_status |{}|".format(self.true_airspeed_status))
        if not (self.true_airspeed_status == 0 or self.true_airspeed_status == 1):
        #    print("BDS error: true_airspeed_status |{}|".format(self.true_airspeed_status))
            return False
        self.true_airspeed = res[46:]
        self.true_airspeed = int(self.true_airspeed, 2)*2
        if self.true_airspeed_status == 0 and self.true_airspeed != 0:
        #    print("BDS error: status error\n")
            return False
        if self.true_airspeed_status == 1:
        #    print("true_airspeed |{}|".format(self.true_airspeed))
            if not (0 <= self.true_airspeed <= 2046):
        #        print("BDS error: true_airspeed |{}|".format(self.true_airspeed))
                return False
        else:
            self.true_airspeed = None    
        
        self.exist = True
        return True
    
    
    def __str__(self):
        if self.exist:
            return (
                f' BDS50: Track and turn report\n'
                f'  Status  (roll angle): {self.roll_angle_status}\n'
                f'  Roll angle: {self.roll_angle} degrees\n'
                f'  Status (track angle): {self.true_track_angle_status}\n'
                f'  True track angle: {self.true_track_angle} degrees\n'
                f'  Status (ground speed): {self.ground_speed_status}\n'
                f'  Ground speed: {self.ground_speed} kt\n'
                f'  Status (track angle rate): {self.track_angle_rate_status}\n'
                f'  Track angle rate: {self.track_angle_rate} degrees/second\n'
                f'  Status (true airspeed): {self.true_airspeed_status}\n'
                f'  True airspeed: {self.true_airspeed} kt\n')
        else:
            return""


######################################
@dataclass
class BDS60:
    magnetic_heading: int
    indicated_airspeed: int
    mach_number: int
    barometric_vertical_rate: int
    inertial_vertical_rate: int
    
    
    def __init__(self):
        self.exist        = False
        #self.len          = 7
        #self.hex          = 0
        self.magnetic_heading_status = 0
        self.magnetic_heading = 0
        self.indicated_airspeed_status = 0
        self.indicated_airspeed = 0
        self.mach_number_status = 0
        self.mach_number = 0
        self.barometric_vertical_rate_status = 0
        self.barometric_vertical_rate = 0
        self.inertial_vertical_rate_status = 0
        self.inertial_vertical_rate = 0
        

    def add_info(self, bds_data: str):
        
        #print("\n---BDS60---")
        res = hexabin(bds_data, 16)
        
        #Magnetic Heading
        self.magnetic_heading_status = res[:1]
        self.magnetic_heading_status = int(self.magnetic_heading_status, 2)
        #print("magnetic_heading_status |{}|".format(self.magnetic_heading_status))
        if not (self.magnetic_heading_status == 0 or self.magnetic_heading_status == 1):
        #    print("BDS error: magnetic_heading_status |{}|".format(self.magnetic_heading_status))
            return False
        self.magnetic_heading = res[1:12]
        self.magnetic_heading = twos_comp(int(self.magnetic_heading, 2), len(self.magnetic_heading))*(90/512)
        if self.magnetic_heading_status == 0 and self.magnetic_heading != 0:
        #        print("BDS error: status error\n")
                return False
        if self.magnetic_heading_status == 1:
        #    print("magnetic_heading |{}|".format(self.magnetic_heading))
            if not (-180 <= self.magnetic_heading <= 180):
        #        print("BDS error: magnetic_heading |{}|".format(self.magnetic_heading))
                return False   
        else:
            self.magnetic_heading = None
        
        #Indicated Airspeed
        self.indicated_airspeed_status = res[12:13]
        self.indicated_airspeed_status = int(self.indicated_airspeed_status, 2)
        #print("indicated_airspeed_status |{}|".format(self.indicated_airspeed_status))
        if not (self.indicated_airspeed_status == 0 or self.indicated_airspeed_status == 1):
        #    print("BDS error: indicated_airspeed_status |{}|".format(self.indicated_airspeed_status))
            return False
        self.indicated_airspeed = res[13:23]
        self.indicated_airspeed = int(self.indicated_airspeed, 2)*1
        if self.indicated_airspeed_status == 0 and self.indicated_airspeed != 0:
        #    print("BDS error: status error\n")
            return False
        if self.indicated_airspeed_status == 1:
        #    print("indicated_airspeed |{}|".format(self.indicated_airspeed))
            if not (0 <= self.indicated_airspeed <= 1023):
        #        print("BDS error: indicated_airspeed |{}|".format(self.indicated_airspeed))
                return False
        else:
            self.indicated_airspeed = None
         
        #Mach Number     
        self.mach_number_status = res[23:24]
        self.mach_number_status = int(self.mach_number_status, 2)
        #print("mach_number_status |{}|".format(self.mach_number_status))
        if not (self.mach_number_status == 0 or self.mach_number_status == 1):
        #    print("BDS error: mach_number_status |{}|".format(self.mach_number_status))
            return False
        self.mach_number = res[24:34]
        self.mach_number = int(self.mach_number, 2)*0.004
        if self.mach_number_status == 0 and self.mach_number != 0:
        #    print("BDS error: status error\n")
            return False
        if self.mach_number_status == 1:
        #    print("mach_number |{}|".format(self.mach_number))
            if not (0 <= self.mach_number <= 4.092):
        #        print("BDS error: mach_number |{}|".format(self.mach_number))
                return False
        else:
            self.mach_number = None
        
        #Barometric Vertical Rate
        self.barometric_vertical_rate_status = res[34:35]
        self.barometric_vertical_rate_status = int(self.barometric_vertical_rate_status, 2)
        #print("barometric_vertical_rate_status |{}|".format(self.barometric_vertical_rate_status))
        if not (self.barometric_vertical_rate_status == 0 or self.barometric_vertical_rate_status == 1):
        #    print("BDS error: barometric_vertical_rate_status |{}|".format(self.barometric_vertical_rate_status))
            return False
        self.barometric_vertical_rate = res[35:45]
        self.barometric_vertical_rate = twos_comp(int(self.barometric_vertical_rate, 2), len(self.barometric_vertical_rate))*32
        if self.barometric_vertical_rate_status == 0 and self.barometric_vertical_rate != 0:
        #    print("BDS error: status error\n")
            return False
        if self.barometric_vertical_rate_status == 1:
        #    print("barometric_vertical_rate |{}|".format(self.barometric_vertical_rate))
            if not (-16384 <= self.barometric_vertical_rate <= 16384):
        #        print("BDS error: barometric_vertical_rate |{}|".format(self.barometric_vertical_rate))
                return False
        else:
            self.barometric_vertical_rate = None
             
        #Inertial Vertical Rate
        self.inertial_vertical_rate_status = res[45:46]
        self.inertial_vertical_rate_status = int(self.inertial_vertical_rate_status, 2) 
        #print("inertial_vertical_rate_status |{}|".format(self.inertial_vertical_rate_status))
        if not (self.inertial_vertical_rate_status == 0 or self.inertial_vertical_rate_status == 1):
        #    print("BDS error: inertial_vertical_rate_status |{}|".format(self.inertial_vertical_rate_status))
            return False
        self.inertial_vertical_rate = res[46:]
        self.inertial_vertical_rate = twos_comp(int(self.inertial_vertical_rate, 2), len(self.inertial_vertical_rate))*32
        if self.inertial_vertical_rate_status == 0 and self.inertial_vertical_rate != 0:
        #    print("BDS error: status error\n")
            return False
        if self.inertial_vertical_rate_status == 1:
        #    print("inertial_vertical_rate |{}|".format(self.inertial_vertical_rate))
            if not (-16384 <= self.inertial_vertical_rate <= 16384):
        #        print("BDS error: inertial_vertical_rate |{}|".format(self.inertial_vertical_rate))
                return False
        else:
            self.inertial_vertical_rate = None
        
        self.exist = True
        return True
    
 
    def __str__(self):
        if self.exist:
            return (
                f' BDS60: Heading and speed report\n'
                f'  Status (for magnetic heading): {self.magnetic_heading_status}\n'
                f'  Magnetic heading: {self.magnetic_heading} degrees\n'
                f'  Status (indicated airspeed): {self.indicated_airspeed_status}\n'
                f'  Indicated airspeed: {self.indicated_airspeed} kt\n'
                f'  Status (for Mach number): {self.mach_number_status}\n'
                f'  Mach number: {self.mach_number}\n'
                f'  Status (barometric altitude rate): {self.barometric_vertical_rate_status}\n'
                f'  Barometric altitude rate: {self.barometric_vertical_rate} ft/min\n'
                f'  Status (inertial vertical velocity) : {self.inertial_vertical_rate_status}\n'
                f'  Inertial vertical velocity: {self.inertial_vertical_rate} ft/min\n')
        else:
            return""


######################################
@dataclass
class ModeS:   
    bds_type: []
    bds44: BDS44() = None
    bds50: BDS50() = None
    bds60: BDS60() = None
    
    
    def __init__(self):
        self.exist        = False
        self.len          = 7
        self.hex          = 0
        self.bds_type     = []
        self.bds44        = BDS44()
        self.bds50        = BDS50()
        self.bds60        = BDS60()
        
        
    def diff_50_60(self, altitude: int):
        #Assuming BDS50 (<200kt)
        #
        speed_diff_50 = abs(self.bds50.ground_speed - self.bds50.true_airspeed)
        if speed_diff_50 >= 100:
            self.bds_type.remove("BDS50")
            self.bds50.exist = False
            #self.bds50 = 0
            
        #Assuming BDS60 (abs(CAS - IAS) < threshold
        #
        # Alt (ft) compulsory -->> Only available in Asterix48, it needs to be 
        # calculated from there by calling the functions defined above
        cas_calculated = calculate_cas(altitude, self.bds60.mach_number, calculate_static_p(altitude))
        speed_diff_60 = abs(cas_calculated  - self.bds60.indicated_airspeed)
        if altitude == 0 and speed_diff_60 >= 100:
            self.bds_type.remove("BDS60")
            self.bds60.exist = False
            #self.bds60 = 0
        return False


    def detect_BDS(self, bds_data: str, altitude: int = 0):
    
        if self.bds44.add_info(bds_data):
            self.bds_type.append("BDS44")
            self.exist = True
    
        if self.bds50.add_info(bds_data):
            self.bds_type.append("BDS50")
            self.exist = True
            
        if self.bds60.add_info(bds_data):
            self.bds_type.append("BDS60")
            self.exist = True
              
        print("\nBDS: {}".format(self.bds_type))
        if self.bds50.exist and self.bds60.exist and not self.bds44.exist:
            #self.bds44 = 0
            self.diff_50_60(altitude)
            self.exist = True
            print("\nBDS (diff): {}".format(self.bds_type))
        
        if not self.bds_type:
            self.bds44 = 0
            self.bds50 = 0
            self.bds60 = 0
            self.bds_type.append("None")
            
            
    def add_info(self, bds_data: str, bds_type: str):
    
        if bds_type == "BDS44":
            self.exist = self.bds44.add_info(bds_data)
            self.bds_type.append(bds_type)
        elif bds_type == "BDS50":
            self.exist = self.bds50.add_info(bds_data)
            self.bds_type.append(bds_type)
        elif bds_type == "BDS60":
            self.exist = self.bds60.add_info(bds_data)
            self.bds_type.append(bds_type)
        else:
            self.bds_type.append("None")
        
        if not self.bds44.exist:
            self.bds44 = None
        if not self.bds50.exist:
            self.bds50 = None
        if not self.bds60.exist:
            self.bds60 = None
            
            
    def __str__(self):
        if self.exist:
            result = ""
            if self.bds44 is not None:
                result += str(self.bds44)
            if self.bds50 is not None:
                result += str(self.bds50)
            if self.bds60 is not None:
                result += str(self.bds60)
            return result
        else:
            return "  None\n"
            
        
######################################################
# DUDA: de donde sale "Temp2" de BDS44
#
def print_in_file(archivo_entrada, archivo_salida, bds_type):
    
    headers_dict = {
        'bds44': "ICAO\tWindSpeed\tWindDirection\tTemp1\tPressure\tHumidity\tTurbulence\tTimestamp\n",
        'bds50': "ICAO\tRollAngle\tTrackAngle\tTrackRate\tGroundSpeed\tTrueAirspeed\tTimestamp\n",
        'bds60': "ICAO\tMagneticHeading\tIndicatedAirspeed\tMach\tVerticalRate(Baro)\tVerticalRate(INS)\tTimestamp\n"
    }
    header = headers_dict.get(bds_type.lower(), "Header no encontrado")
    data_dict = {}
    
    try:
        with open(archivo_entrada, 'r') as file1, open(archivo_salida, 'w') as file2:
           
            file2.write(header)
            # Leer línea por línea
            for linea in file1:
                # Parsear la línea usando espacio como delimitador
                # [Time, BDS, BDS_Type, Address]
                elementos = linea.split()
                
                # Hacer algo con los elementos, por ejemplo, imprimirlos
                print("{} | {}".format(elementos[2],bds_type))
                
                if elementos[2] == bds_type:
                    
                    print("ME SIRVE:\n")
                    bds_data = ModeS()
                    bds_data.add_info(elementos[1], bds_type)
                    #print(bds_type)
                    
                    print(f"Data: |{bds_data.exist}|{elementos[1]}\n")
                    tipo_de_variable = type(bds_data)

                    # Imprimir el tipo de la variable
                    print("El tipo de la variable es:", tipo_de_variable)

                    #Write BDS elements
                    #data_dict = asdict(bds_data.bds60)
                    
                    if bds_data.exist:
                        
                        #Write OACI element
                        file2.write(elementos[3] +"\t")
                        data_dict = asdict(getattr(bds_data, bds_type.lower()))
                        for clave, val in data_dict.items():
                            if clave == "fom": 
                                continue
                            print(val)
                            #if val == 0:
                            #    break
                            file2.write(str(val) + "\t")
                        data_dict = {}
                        
                        #Write Timestamp element
                        file2.write(elementos[0] + "\n")
                        #if val == 0:
                        #    break
                        #print(data_dict)
                    else:
                        logging.error(f'Message BDS not decoded: {linea}')
    except FileNotFoundError:
        print("Uno de los archivos no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        

######################################################

def bds_to_file (file, messages_asterix48):   
    
    header = "Time\tBDS\tBDS_Type\tAddress\tTarget_ID\n"   # DUDA -->> Target_ID??
    atributos_a_guardar = ["item140", "item220", "item240", "item250"]       
    data_dict = {}
    values = []
    i, j = 0, 0
    try:
        with open(file, "w") as archivo:
            archivo.write(header)
            for i in range(len(messages_asterix48.messages)):
                for j in range(len(messages_asterix48.messages[i].blocks)):
                    mensaje = messages_asterix48.messages[i].blocks[j]
                    datos_a_guardar = ({attr: getattr(mensaje, attr) 
                                        for attr in atributos_a_guardar})
               
                    for item in atributos_a_guardar:
                        if datos_a_guardar[item].exist:
                            data_dict = asdict(datos_a_guardar[item])
                            #print(f"DICT: |{data_dict}|\n")
                            for valor in data_dict.values():
                                
                                if item == "item140":
                                    item140 = str(valor)
                                
                                if item == "item220":
                                    item220 = str(valor)
                                    
                                if item == "item240":
                                    item240 = str(valor)
                                
                                if item == "item250":
                                    
                                    for elemento in valor:
                                        values.append(item140)
                                        for clave, val in elemento.items():
                                            if clave == "bdsdata": 
                                                continue
                                            values.append(str(val))
                                        values.append(item220)
                                        values.append(item240)
                                        values_str = '\t'.join(values)
                                        archivo.write(values_str + "\n")
                                        data_dict, values, values_str = {}, [], ""
                            data_dict = {}
                        elif item == "item140":
                            item140 = str(None)
                            
                        elif item == "item240":
                            item240 = str(None)
                    item140, item220, item240 = "", "", ""
                        
        print("Data dumped to txt!\n")

    except Exception as e:
        print(f"Error dumping to txt: {e}")    
        

######################################################
