# Valerie Manfull and Tom Marquez
# CSCE 490
# Final Project
# Anchorage Solar Siting Survey
#
#
import arcpy
from arcpy import env
import arcpy.sa as sa
import numpy as np
import math
import os

# Tom wrote get_workspace
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

# Tom wrote get_raster_path
def get_raster_path():
    """Similar method as above, this one just returns the location of the raster file, 
    since the raster file will more than likely not be in the same directory of the workspace
    """
    cwd = os.getcwd()
    cwd_split = cwd.split("\\")
    if cwd_split[2] == "tommarquez":
        return 'C:/Users/tommarquez/Documents/School/Geospatial-Programming_files/1659_2635/1659_2635.tif'
    return 'C:/Users/Valerie/Desktop/square_tiff/1659_2635.tif' # Done TODO: Valerie, add the full path of your raster file here

# Tom wrote initial code
# Tom and Valerie together added elevation
# Tom moved this into a method
# Valerie added out_cursor, so results would be in a shape file
#
def building_array(x_coords, y_coords, shape_file, out_shape):
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
    
    # Thresholds of elevation and area
    elev_thresh = 30
    area_thresh = 2000
    
    # Array to hold all of the buildings downtown
    downtown_buildings = []
    # Variable that stores the last seen building
    # Prevents a polygon being added to the array more than once
    # building_name = ""
    fields = ["FID", "SHAPE@XY", "CURRENT_TI", "ELEVATION", "SHAPE@"]
    # max_area = 0
    out_cursor = arcpy.da.InsertCursor(out_shape, fields)
    with arcpy.da.SearchCursor(shape_file, fields) as cursor:
        for row in cursor:
            shape = row[1]
            # shape[0] shape[1] is the x y of the centroid (?) of the polygon (building)
            if shape[0] > x_coords[0] and shape[0] < x_coords[1] and shape[1] > y_coords[0] and shape[1] < y_coords[
                1] and row[3] > elev_thresh:
                
                area = row[4].area
                if area > area_thresh:
                    total_area = total_area + area
                    downtown_buildings.append(row)
                    out_cursor.insertRow(row)
                    total_panels = total_panels + math.floor(area / solar_panel)
                        
    del row
    del cursor
    del out_cursor
    
    return downtown_buildings, total_area, total_panels

# Tom wrote is_south_building_taller
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

# main code initially written by Tom
# Most was written together
# Valerie added out_fc shapefile, spatial reference, and standard deviation stuff
# Standard dev stuff should be in a method ... 

env.workspace = get_workspace()
fc = "buildings.shp"
out_fc = "anch_good_sites.shp"
if arcpy.Exists(out_fc):
    arcpy.Delete_management(out_fc)

# Need to set the Spatial Reference of the out_fc. 
sr = 'NAD 1983 StatePlane Alaska 4 FIPS 5004 Feet'

arcpy.CreateFeatureclass_management(env.workspace, out_fc, "Polygon", fc, "", "","", sr)
 
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
# Tom's original
#x_coords = [1655760.854, 1661815.541]
#y_coords = [2637870.993, 5637870.993]
# Valerie adjusted the coords so they would be part of downtown
#x_coords = [1655468.109, 1663714.632]
#y_coords = [2635419.875, 2638805.296]

# x, y coords for buildings in NLCD raster 1659_2635.tif 
x_coords = [1659059.606, 1661932.002]
y_coords = [2635011.822, 2637910.260]

# Array to hold all of the buildings downtown, var for total area, and var for total panels in given area
downtown_buildings, total_area, total_panels = building_array(x_coords, y_coords, fc, out_fc)

# add field to shape for the std values, red, green, blue, for each building  
arcpy.AddField_management(out_fc, 'std_red', "FLOAT")
arcpy.AddField_management(out_fc, 'std_green', "FLOAT")
arcpy.AddField_management(out_fc, 'std_blue', "FLOAT")    


is_south_building_taller(fc, x_coords, y_coords)


# loop through all buildings in array that are in the raster we are looking at
# eventually, we will look at all the rasters ...

#for buildings in downtown_buildings: # was looping through array

# Valerie added the standard deviation fields to the out_fc,
#    changed following code to read rows in out_fc,and update rows with the RGB stds
# this could (should) be moved into its own method ...
with arcpy.da.UpdateCursor(out_fc, ["SHAPE@", "std_red", "std_green", "std_blue"]) as cursor:
    for row in cursor:
        # array to hold the values that will be used to find the standard dev
        sdarray_green = []
        sdarray_red = []
        sdarray_blue = []
        bldpoly = row[0]
        # add/sub 1 to include whole building
        bxmin = int(bldpoly.extent.XMin)-1
        bxmax = int(bldpoly.extent.XMax)+1
        bymin = int(bldpoly.extent.YMin)-1
        bymax = int(bldpoly.extent.YMax)+1
        
    
        # Loop through the building in the downtown_buildings array
        # and append all the green, red, and blue values to the sdarray
        for j in range (bymin, bymax):
            for i in range (bxmin, bxmax):
                if (arcpy.Point(i,j).within(bldpoly)):
                    #print (nlcd[1][i-bxmin][j-bymin])
                    sdarray_green.append(nlcd[1][i-bxmin][j-bymin])
                    sdarray_red.append(nlcd[0][i-bxmin][j-bymin])
                    sdarray_blue.append(nlcd[2][i-bxmin][j-bymin])
                    
        # Convert to numpy array to take standard dev
        arr_green = np.array(sdarray_green)
        arr_red = np.array(sdarray_red)
        arr_blue = np.array(sdarray_blue)
        #print ('green: ' + str(np.std(arr_green)) + ' red: ' + str(np.std(arr_red)) + ' blue: ' + str(np.std(arr_blue)))
        #print len(sdarray_green)
    
    # Update the cursor row with each std
        row[1] = np.std(arr_red)
        row[2] = np.std(arr_green)
        row[3] = np.std(arr_blue)
        cursor.updateRow(row)
        
del row
del cursor



# convert building polygon to a raster
# nlcd[x][y] is centroid? of the building. 


    