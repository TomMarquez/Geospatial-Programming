
import arcpy
from arcpy import env

env.workspace = "C:/Users/Valerie/Desktop/buildings"
fc = "buildings.shp"

# Industrial panels are 77" x 39", so 20.85 sq ft
solar_panel = 20.85

# Variables to hold the x and y coordinates of downtown
x_coords = [1655468.109, 1663714.632]
y_coords = [2635419.875, 2638805.296]
#x_coords = [1655760.854, 1661815.541]
#y_coords = [2637870.993, 5637870.993]
total_area = 0.0
total_panels = 0

# Array to hold all of the buildings downtown
downtown_buildings = []

# Variable that stores the last seen building
# Prevents a polygon being added to the array more than once
building_name = ""
fields = ["SHAPE@XY", "CURRENT_TI", "ELEVATION", "SHAPE@"]

# max_area = 0
with arcpy.da.SearchCursor(fc, fields) as cursor:
    for row in cursor:
        shape = row[0]
       # print shape.area
        if shape[0] > x_coords[0] and shape[0] < x_coords[1] and shape[1] > y_coords[0] and shape[1] < y_coords[1]:
            # Does not add blank polygons to the array or buildings already added
            # Will probably need to add the blank polygons since they are buildings downtown, but
            # just for testing, I only added the buildings that have names associated with the polygon.
            if row[1] != " " and building_name != row[1]:
                area = row[3].area
                # print area
                if area > 2000:
                    total_area = total_area + area
                    downtown_buildings.append(row)
                    total_panels = total_panels + math.floor(area/solar_panel)
                    # building_name = row[1]
                
# Print all the buildings in the array
for buildings in downtown_buildings:
    print(buildings[1] + " " + str(buildings[3].area))
    
print ("number of panels  in downtown: " + str(total_panels))