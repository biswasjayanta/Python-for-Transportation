import arcpy
import pandas as pd
import os

def getParameterInfo():
    # Define input and output parameters for the tool
    param0 = arcpy.Parameter(
        displayName="Workspace",
        name="in_workspace",
        datatype="DEWorkspace",
        parameterType="Required",
        direction="Input")

    param1 = arcpy.Parameter(
        displayName="Class Name",
        name="class_name",
        datatype="GPString",
        parameterType="Required",
        direction="Input")

    param2 = arcpy.Parameter(
        displayName="Class Value",
        name="class_value",
        datatype="GPLong",
        parameterType="Required",
        direction="Input")

    param3 = arcpy.Parameter(
        displayName="Output File",
        name="out_file",
        datatype="DEFile",
        parameterType="Required",
        direction="Output")
    param3.filter.list = ['txt', 'csv']

    return [param0, param1, param2, param3]

def count_pixels_for_class(raster, class_name, class_value, output_csv):
    # Check if the raster has the required field
    fields = [f.name for f in arcpy.ListFields(raster)]
    if class_name not in fields:
        print(f"Field '{class_name}' not found in raster {raster}. Skipping.")
        return
    
    # Check if the class_value exists in the raster
    class_values = set()
    with arcpy.da.SearchCursor(raster, [class_name]) as cursor:
        for row in cursor:
            class_values.add(row[0])
    
    if class_value not in class_values:
        print(f"Class value '{class_value}' not found in raster {raster}. Skipping.")
        return
    
    # Query the table to find pixel counts for the class
    pixel_count = []
    with arcpy.da.SearchCursor(raster, [class_name, "Count"]) as cursor:
        for row in cursor:
            if row[0] == class_value:
                pixel_count.append({"Raster": raster, "Class": row[0], "Pixel Count": row[1]})

    # Convert results to a DataFrame
    df = pd.DataFrame(pixel_count)

    # If there are results, append to CSV file
    if not df.empty:
        df.to_csv(output_csv, mode='a', header=not os.path.exists(output_csv), index=False)
        print(f"Pixel count for {raster} exported to {output_csv}")
    else:
        print(f"No pixels found for class {class_value} in {raster}")

# Get parameter values from ArcGIS
workspace = arcpy.GetParameterAsText(0)  # Workspace input
class_name = arcpy.GetParameterAsText(1)  # Class name input
class_value = int(arcpy.GetParameterAsText(2))  # Class value input
output_csv = arcpy.GetParameterAsText(3)  # Output CSV file

# Set the workspace for ArcPy
arcpy.env.workspace = workspace

# Clear the CSV file if it already exists
if os.path.exists(output_csv):
    os.remove(output_csv)

# Get a list of raster datasets in the workspace
rasters = arcpy.ListRasters()

# Loop through each raster in the list
for raster in rasters:
    count_pixels_for_class(raster, class_name, class_value, output_csv)
