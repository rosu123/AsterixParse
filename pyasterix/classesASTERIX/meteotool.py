#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 20:27:47 2024

@author: rodrigo
"""


import math
import pandas as pd
from datetime import datetime, timedelta
from fastmeteo import Grid
from tqdm import tqdm
import warnings



# Constants of the standard atmospheric model
p0 = 101325  # Air pressure at sea level (Pa)
ρ0 = 1.225   # Air density at sea level (kg/m3)
L = 0.0065   # Rate of temperature variation with altitude in K/m
a0 = 340.29  # Speed of sound at sea level (m/s)
T0 = 288.15  # Temperature at sea level (K)
R  = 287.05  # Gas constant at sea level (J/(kg·K))
g  = 9.8066  # Acceleration due to gravity in m/s²



###############################################################################
# TEMPERATURE (T)

# ESTA FUNCIÓN ME SACA VALORES SIEMPRE MÁS ALTOS DE P QUE LOS REALES --> ??¿¿ 
# ¡¡ESTA NO LA VAMOS A USAR POR AHORA, MEJOR LA DE ABAJO!!
#
def calculate_pressure_altitude(altitude_ft):

    # Convert altitude from feet to meters
    altitude_meters = altitude_ft * 0.3048

    # Calculate static pressure
    #pressure_1 = p0 * (1 - (L * altitude_meters) / T0) ** (g / (R * L))
    
    pressure = p0 * math.exp(-(g * altitude_meters) / (R * T0))

    return pressure

# EXAMPLE

#altitude_ft = 35000

#pressure_1 = calculate_pressure_altitude(altitude_ft)


# Calculate Atmospheric pressure (static)
#
def calculate_static_p(altitude_ft):

    # Convert altitude from feet to meters
    altitude_meters = altitude_ft * 0.3048

    # Calculate static pressure
    pressure = p0 * (1 - (L * altitude_meters) / T0) ** (g / (R * L))

    return pressure

# EXAMPLE

#altitude_ft = 35000

#pressure_2 = calculate_static_p(altitude_ft)


# Calculate Temperature
#
def calculate_temperature(mach, v_tas, altitude_ft, v_ias):
    
    #Convert from knots to m/s
    v_tas_m = v_tas * 0.514444
    v_ias_m = v_ias * 0.514444
    
    if mach < 0.3:
        pressure = calculate_static_p(altitude_ft)
        temperature = (v_tas_m**2 * pressure) / (v_ias_m**2 * ρ0 *  R)
        
    else:
        temperature = (v_tas_m**2 * T0) / (mach**2 * a0**2)
    
    return temperature

# EXAMPLE

#mach = 0.58            # Mach
#v_tas = 368.0          # TrueAirspeed (knots)
#altitude_ft = 14900.0  # Altitude (ft)
#v_ias = 294.0          # IndicatedAirspeed (knots)

#temperature = calculate_temperature(mach, v_tas, altitude_ft, v_ias)



###############################################################################
# TRUE AIRSPEED (Vtas)

# Calculate Air density
#
def calculate_ρ(pressure, temperature):
    
    ρ = pressure / (R * temperature)
    
    return ρ


# Calculate Vtas
#
def calculate_v_tas(mach, altitude_ft, v_ias, temperature):
    
    #Convert from knots to m/s
    v_ias_m = v_ias * 0.514444
    
    if mach < 0.3:
        pressure = calculate_static_p(altitude_ft)
        ρ = calculate_ρ(pressure, temperature)
        v_tas_m = v_ias_m * math.sqrt(ρ0 / ρ)
        
    else:
        v_tas_m = mach * a0 * math.sqrt(temperature / T0)
    
    #Convert to knots
    v_tas_m = v_tas_m/0.514444
    
    return v_tas_m

# EXAMPLE

#mach = 0.58            # Mach
#v_tas = 368.0          # TrueAirspeed (knots)
#altitude_ft = 14900.0  # Altitude (ft)
#v_ias = 294.0          # IndicatedAirspeed (knots)

#v_tas_model = calculate_v_tas(mach, altitude_ft, v_ias, temperature)



###############################################################################
# Wind (Vw)

def calculate_wind_vector(TAS, heading, GS, track_angle): 
    # Convert track angle and heading to radians
    track_angle_rad = math.radians(track_angle)
    heading_rad = math.radians(heading)
    
    # Calculate the angle between the wind direction and the direction the plane is heading
    wind_direction = math.degrees(math.atan2((GS * math.sin(track_angle_rad)) - (TAS * math.sin(heading_rad)),
                                             (GS * math.cos(track_angle_rad)) - (TAS * math.cos(heading_rad))))
    
    # Calculate wind speed
    wind_speed = math.sqrt((GS * math.cos(track_angle_rad) - TAS * math.cos(heading_rad))**2 +
                           (GS * math.sin(track_angle_rad) - TAS * math.sin(heading_rad))**2)
    
    return wind_speed, wind_direction

# EXAMPLE

#TAS = v_tas # True Airspeed in knots
#GS = 420  # Ground Speed in knots
#track_angle = 105.1171875  # Track angle in degrees
#heading = 115.6640625  # Heading in degrees

#wind_speed, wind_direction = calculate_wind_vector(TAS, heading, GS, track_angle)
#print("Wind speed:", wind_speed, "knots")
#print("Wind direction:", wind_direction, "degrees")


# Convert polar to cartesian (u, v) coordinates from North clockwise as angle reference
def polar_to_cartesian(magnitude, angle):
    # Convert angle to radians
    angle_rad = math.radians(angle)
    # Calculate cartesian coordinates
    x = magnitude * math.sin(angle_rad)
    y = magnitude * math.cos(angle_rad)
    return x, y

# EXAMPLE

#wind_speed_u, wind_speed_v = polar_to_cartesian(wind_speed, wind_direction)



##############################################################################
# Format time to "2019-12-20T00:00:01" (date of our example data)

def time_format(time):
    delta = timedelta(seconds=time)
    midnight = datetime(1, 1, 1, 0, 0, 0)
    date_time = midnight + delta

    return ("2019-12-20T{:02d}:{:02d}:{:02d}\n".format(date_time.hour, 
             date_time.minute, date_time.second))



##############################################################################

###############################################
#####  Merge items CAT21 and BDS50 BDS60  #####
###############################################


def merge_data(fileCAT21: str, fileBDS50: str, fileBDS60: str, output_file: str, max_dev: float):

    column1 = 'time_rec_pos'
    column2 = 'Timestamp'
    column3 = 'Timestamp'
    
    data1 = pd.read_csv(fileCAT21, delimiter='\t', engine='python')
    data2 = pd.read_csv(fileBDS50, delimiter='\t', engine='python')
    
    # Drop all rows with Nan merge column
    data1 = data1.dropna(subset=[column1])
    data2 = data2.dropna(subset=[column2])
    
    # Sort de df by merge column
    data1 = data1.sort_values(column1)
    data2 = data2.sort_values(column2)
    
    # Merge data CAT21 and BDS50
    merged_data = pd.merge_asof(
        data1, data2,
        left_on=column1, right_on=column2,
        direction='nearest', tolerance=max_dev
    )
    
    # Only rows with "target_addr = ICAO" 
    merged_data_2 = merged_data[merged_data['target_addr'] == merged_data['ICAO']]
    
    
    data3 = pd.read_csv(fileBDS60, delimiter='\t', engine='python')
    
    # Drop all rows with Nan merge column
    data3 = data3.dropna(subset=[column3])
    
    # Sort de df by merge column
    data3 = data3.sort_values(column3)

    # Merge previous merge and BDS60
    merged_data_total = pd.merge_asof(
        merged_data_2, data3,
        left_on=column1, right_on=column3,
        direction='nearest', tolerance=max_dev
    )
    
    # Drop all rows with Nan "target_id" column 
    merged_data_total = merged_data_total.dropna(subset=['target_id'])
    
    # Only rows with "target_addr = ICAO" 
    merged_data_total_2 = merged_data_total[merged_data_total['target_addr'] == merged_data_total['ICAO_y']]
    
    # Drop all rows in which needed info is Nan
    column_list = ['geom_height', 'GroundSpeed', 'TrueAirspeed', 'IndicatedAirspeed', 
                   'Mach', 'TrackAngle', 'GroundSpeed', 'MagneticHeading']
    
    for column in column_list: 
        merged_data_total_2 = merged_data_total_2.dropna(subset=[column])

    # Save merge
    merged_data_total_2.to_csv(output_file, sep='\t', index=False)
    
    
    
##############################################################################

###################################
#####  Calculate meteo index  #####
###################################


def calculate_meteo(input_file: str, output_file: str, local_meteo_grid: str):
    
    df = pd.read_csv(input_file, delimiter='\t')
    
    #print(df.head())
    # Ignore "DeprecationWarning: parsing timezone aware datetimes is deprecated" warning
    # It comes from mmg.interpolate(flight_1) call (fastmeteo package)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    # Define the location for local store
    # IMP: mount /Data disc before run
    mmg = Grid(local_store=local_meteo_grid)
    
    info = ['Timestamp', 'Latitude', 'Longitude', 'Altitude', 
            'Temperature_BDS', 'Wind_u_BDS', 'Wind_v_BDS', 
            'Temperature_ERA5', 'Wind_u_ERA5', 'Wind_v_ERA5']
    
    #df_meteo = pd.DataFrame(columns=info)
    
    lst = []
    num_rows = len(df)
    #for msg in range(num_rows):
    for msg in tqdm(range(num_rows), desc="Progress", 
                    unit=" messages"):
    
        #print(df.iloc[msg])
        mach = df.loc[msg, 'Mach']
        v_tas = df.loc[msg, 'TrueAirspeed']
        heading = df.loc[msg, 'MagneticHeading']
        v_gs = df.loc[msg, 'GroundSpeed']
        track_angle = df.loc[msg, 'TrackAngle']
        altitude_ft = df.loc[msg, 'geom_height']
        v_ias = df.loc[msg, 'IndicatedAirspeed']
        
        temperature = calculate_temperature(mach, v_tas, altitude_ft, v_ias)
        
        v_tas_model = calculate_v_tas(mach, altitude_ft, v_ias, temperature)
        wind_speed, wind_direction = calculate_wind_vector(v_tas_model, heading, v_gs, track_angle)
        
        # Meteorological Vw is opposite of aeronautical Vw (we shift the direction of the wind vector by 180 ° to obtain the wind direction)
        #if wind_direction <= 180:
        #    wind_direction += 180
        #else:
        #    wind_direction -= 180
        
        wind_speed_u, wind_speed_v = polar_to_cartesian(wind_speed, wind_direction) #knots
        
        # Convert to m/s (ERA5 format)
        wind_speed_u, wind_speed_v = wind_speed_u * 0.5144444444, wind_speed_v * 0.5144444444 
        
        #print(f"\nBDS:   Temperature = {temperature} | Wind_speed_u = {wind_speed_u} | Wind_speed_v = {wind_speed_v}")
        
        time_era5 = time_format(df.loc[msg, 'time_rec_pos'])
        latitude = df.loc[msg, 'latitude']
        longitude = df.loc[msg, 'longitude']
        
        flight_1 = pd.DataFrame(
            {
                "timestamp": [time_era5],
                "latitude": [latitude],
                "longitude": [longitude],
                "altitude": [altitude_ft],
            }
        )
        
        flight_new_1 = mmg.interpolate(flight_1)
        
        #print(f"ERA5:  Temperature = {flight_new_1.loc[0, 'temperature']} | Wind_speed_u = {flight_new_1.loc[0, 'u_component_of_wind']} | Wind_speed_v = {flight_new_1.loc[0, 'v_component_of_wind']}\n")
        
        # Add row to list
        new_data = {
            'Timestamp': time_era5,
            'Latitude': latitude,
            'Longitude': longitude,
            'Altitude': altitude_ft,
            'Temperature_BDS': temperature,
            'Wind_u_BDS': wind_speed_u,
            'Wind_v_BDS': wind_speed_v,
            'Temperature_ERA5': flight_new_1.loc[0, 'temperature'],
            'Wind_u_ERA5': flight_new_1.loc[0, 'u_component_of_wind'],
            'Wind_v_ERA5': flight_new_1.loc[0, 'v_component_of_wind']
        }
        lst.append(new_data)
        
        #if msg > 5:
        #    break
    
    # Add list to dataframe (calculated on list and only once added to dataframe 
    # because computational efficiency reason)
    df_meteo = pd.DataFrame(lst, columns=info)
    
    # Save dataframe on txt
    df_meteo.to_csv(output_file, sep='\t', index=False)
    
    
    


















