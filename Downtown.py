#################################################################
## Purpose: This program hopefully will only choose the polygons
##          that are only downtown.
##          Pick polygons between these 4 coordinates:
##          1655760.854, 2637870.993 - top left
##          1655760.854, 2635709.534 - bottom left
##          1661815.541, 2635709.354 - bottom right
##          1661815.541, 5637870.993 - top right
##
##
#################################################################


import arcpy
from arcpy import env

env.workspace = "C:/Users/tommarquez/Documents/School/CSCE412/Geospatial-Programming/buildings"
fc = "buildings.shp"

# Variables to hold the x and y coordinates of downtown
x_coords = [1655760.854, 1661815.541]
y_coords = [2637870.993, 5637870.993]

# Array to hold all of the buildings downtown
downtown_buildings = []

# Variable that stores the last seen building
# Prevents a polygon being added to the array more than once
building_name = ""
fields = ["SHAPE@XY", "CURRENT_TI", "ELEVATION"]

with arcpy.da.SearchCursor(fc, fields) as cursor:
    for row in cursor:
        shape = row[0]
        if shape[0] > x_coords[0] and shape[0] < x_coords[1] and shape[1] > y_coords[0] and shape[1] < y_coords[1]:
            # Does not add blank polygons to the array or buildings already added
            # Will probably need to add the blank polygons since they are buildings downtown, but
            # just for testing, I only added the buildings that have names associated with the polygon.
            if row[1] != " " and building_name != row[1]:
                downtown_buildings.append(row)
                building_name = row[1]
                
# Print all the buildings in the array
for buildings in downtown_buildings:
    print(buildings[1])