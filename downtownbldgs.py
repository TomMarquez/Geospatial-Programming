
import arcpy
from arcpy import env
import arcpy.sa as sa
import numpy as np
import math
import os

def get_workspace():
    """This method simply checks the current directory of the working computer
    and returns the workspace.
    This is a convenience method so we don't have to change the path of the workspace
    """
    cwd = os.getcwd()
    cwd_split = cwd.split("\\")
    if cwd_split[2] == "tommarquez":
        return "C:/Users/tommarquez/Documents/School/Geospatial-Programming/buildings"
    return "C:/Users/Valerie/Desktop/buildings"

def get_raster_path():
    """Similar method as above, this one just returns the location of the raster file, 
    since the raster file will more than likely not be in the same directory of the workspace
    """
    cwd = os.getcwd()
    cwd_split = cwd.split("\\")
    if cwd_split[2] == "tommarquez":
        return 'C:/Users/tommarquez/Documents/School/Geospatial-Programming_files/1659_2635/1659_2635.tif'
    return '1659_2635.tif' # TODO: Valerie, add the full path of your raster file here

def building_array(x_coords, y_coords, shape_file):
    """This method takes in the x and y coordinates that define the area of focus of the 
    shape file.
    Returns: a building array, total usable area, and the amount of solar panels that can 
    fit in the given area. 
    TODO: May need to take out the total amount of solar panels. This may need to go into
    another method...maybe
    """
    # Industrial panels are 77" x 39", so 20.85 sq ft
    solar_panel = 20.85
    total_area = 0.0
    total_panels = 0
    elev_thresh = 30
    area_thresh = 2000
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
            # shape[0] shape[1] is the x y of the centroid of the polygon (building)
            if shape[0] > x_coords[0] and shape[0] < x_coords[1] and shape[1] > y_coords[0] and shape[1] < y_coords[
                1] and row[2] > elev_thresh:
                # row[2] is elevation, want to be at least 30
                # Does not add blank polygons to the array or buildings already added
                # Will probably need to add the blank polygons since they are buildings downtown, but
                # just for testing, I only added the buildings that have names associated with the polygon.
                if row[1] != " " and building_name != row[1]:
                    area = row[3].area
                    if area > area_thresh:
                        total_area = total_area + area
                        downtown_buildings.append(row)
                        total_panels = total_panels + math.floor(area / solar_panel)
    return downtown_buildings, total_area, total_panels

def is_south_building_taller(shape_file, x_coords, y_coords):
    """This method should return true if building south of the building at
    x y coords is taller
    This method converts the shape file to raster and uses a moving window to look
    at the polygon south
    """
    raster_ext = 'raster.tif'
    if arcpy.Exists(raster_ext):
        arcpy.Delete_management(raster_ext)
        print("WARNING: deleting file " + raster_ext)
    raster_file = arcpy.FeatureToRaster_conversion(shape_file, "elevation", raster_ext)
    print(raster_file)

env.workspace = get_workspace()
fc = "buildings.shp"
# get access to a DEM raster dataset
arcpy.CheckOutExtension("Spatial")
#create raster object

#valerie's raster data location: '1659_2635.tif'

# Tom's raster data location: C:\Users\tommarquez\Documents\School\Geospatial-Programming_files\1659_2635\1659_2635.tif
nlcd_rstr = sa.Raster(get_raster_path())

arcpy.CheckInExtension("Spatial")

# convert to numpy array
nlcd = arcpy.RasterToNumPyArray(nlcd_rstr)

# Variables to hold the x and y coordinates of downtown
#x_coords = [1655468.109, 1663714.632]
#y_coords = [2635419.875, 2638805.296]
# Tom's original
#x_coords = [1655760.854, 1661815.541]
#y_coords = [2637870.993, 5637870.993]

# buildings in 1659_2635.tif
x_coords = [1659059.606, 1661932.002]
y_coords = [2635011.822, 2637910.260]

# Array to hold all of the buildings downtown, var for total area, and var for total panels in given area
downtown_buildings, total_area, total_panels = building_array(x_coords, y_coords, fc)

is_south_building_taller(fc, x_coords, y_coords)

# Print all the buildings in the array
#for building in downtown_buildings:
    #print(building[1] + " area: " + str(building[3].area) + " elevation: " + str(building[2]))

#for building in downtown_buildings:
#print (downtown_buildings[0][3])

# add/sub 1 to include whole building
bxmin = int(downtown_buildings[0][3].extent.XMin)-1
bxmax = int(downtown_buildings[0][3].extent.XMax)+1
bymin = int(downtown_buildings[0][3].extent.YMin)-1
bymax = int(downtown_buildings[0][3].extent.YMax)+1

# array to hold the green values that will be used to find the standard dev
sdarray = []

# Loop through the first building in the downtown_buildings array
# and append all the green values to the sdarray
for j in range (bymin, bymin+ 10):  #bymax):
    for i in range (bxmin, bxmin + 10):  #bxmax):
        if (arcpy.Point(i,j).within(downtown_buildings[0][3])):
            #print (nlcd[1][i-bxmin][j-bymin])
            sdarray.append(nlcd[1][i-bxmin][j-bymin])
            
# Convert to numpy array to take standard dev
arr = np.array(sdarray)
#print np.std(arr)


# convert building polygon to a raster
# nlcd[x][y] is centroid? of the building. Can we refer to that building, and get the standard deviation?


    