
import arcpy
from arcpy import env
import arcpy.sa as sa
import numpy as np


env.workspace = "C:/Users/Valerie/Desktop/buildings"
fc = "buildings.shp"

# get access to a DEM raster dataset
arcpy.CheckOutExtension("Spatial")
#create raster object 
nlcd_rstr = sa.Raster('1659_2635.tif')

print 'num bands:', nlcd_rstr.bandCount

arcpy.CheckInExtension("Spatial")


# convert to numpy array
nlcd = arcpy.RasterToNumPyArray(nlcd_rstr)
print type(nlcd)

print(nlcd.shape)

# Industrial panels are 77" x 39", so 20.85 sq ft
solar_panel = 20.85

# Variables to hold the x and y coordinates of downtown
#x_coords = [1655468.109, 1663714.632]
#y_coords = [2635419.875, 2638805.296]
# Tom's original
#x_coords = [1655760.854, 1661815.541]
#y_coords = [2637870.993, 5637870.993]

# buildings in 1659_2635.tif
x_coords = [1659059.606, 1661932.002]
y_coords = [2635011.822, 2637910.260]
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
       # shape[0] shape[1] is the x y of the centroid of the polygon (building)
        if shape[0] > x_coords[0] and shape[0] < x_coords[1] and shape[1] > y_coords[0] and shape[1] < y_coords[1] and row[2] >30:
            # row[2] is elevation, want to be at least 30
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
#for building in downtown_buildings:
    #print(building[1] + " area: " + str(building[3].area) + " elevation: " + str(building[2]))
    
#print ("number of panels  in downtown: " + str(total_panels))

#for building in downtown_buildings:
#print (downtown_buildings[0][3])

# add/sub 1 to include whole building
bxmin = int(downtown_buildings[0][3].extent.XMin)-1
bxmax = int(downtown_buildings[0][3].extent.XMax)+1
bymin = int(downtown_buildings[0][3].extent.YMin)-1
bymax = int(downtown_buildings[0][3].extent.YMax)+1

sdarray = []

for j in range (bymin, bymin+ 10):  #bymax):
    for i in range (bxmin, bxmin + 10):  #bxmax):
        if (arcpy.Point(i,j).within(downtown_buildings[0][3])):
            np.append(rgbarray, nlcd[1][i-bxmin][j-bymin])  # this not working?
            print (nlcd[1][i-bxmin][j-bymin])
            sdarray.append(nlcd[1][i-bxmin][j-bymin])
            

arr = np.array(sdarray)
print np.std(arr)




#out_file = "shape_raster_conv.tiff"
#thingy = PolygonToRaster_conversion(downtown_buildings[0][3], "SHAPE@", outfile)

# convert building polygon to a raster
# nlcd[x][y] is centroid? of the building. Can we refer to that building, and get the standard deviation?


    