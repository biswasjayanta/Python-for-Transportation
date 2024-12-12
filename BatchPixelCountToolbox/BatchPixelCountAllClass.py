import arcpy
import pandas as pd
import os

def getParameterInfo():
    # First parameter: Workspace
    param0 = arcpy.Parameter(
        displayName="Workspace",
        name="in_workspace",
        datatype="DEWorkspace",
        parameterType="Required",
        direction="Input")
    
    # Second parameter: Class Name
    param1 = arcpy.Parameter(
        displayName="Class Name",
        name="class_name",
        datatype="GPString",
        parameterType="Required",
        direction="Input")
    
    # Third parameter: Output File
    param2 = arcpy.Parameter(
        displayName="Output File",
        name="out_file",
        datatype="DEFile",
        parameterType="Required",
        direction="Output")
    param2.filter.list = ['txt', 'csv']
    
    return [param0, param1, param2]

def count_pixels_for_all_values(raster, class_name, output_csv):
    try:
        # Check if the raster has the required field
        fields = [f.name for f in arcpy.ListFields(raster)]
        if class_name not in fields:
            print(f"Field '{class_name}' not found in raster {raster}. Skipping.")
            return
        
        # Query the table for all classes
        pixel_count = []
        with arcpy.da.SearchCursor(raster, [class_name, "Count"]) as cursor:
            for row in cursor:
                pixel_count.append({"Raster": raster, "Class": row[0], "Pixel Count": row[1]})
        
        # Convert results to a DataFrame
        df = pd.DataFrame(pixel_count)
        
        # Append results to CSV file
        if not df.empty:
            df.to_csv(output_csv, mode='a', header=not os.path.exists(output_csv), index=False)
            print(f"Pixel counts for {raster} exported to {output_csv}")
        else:
            print(f"No pixel data found in {raster}")
    except Exception as e:
        print(f"Error processing raster {raster}: {e}")

# Get parameter values from ArcGIS
workspace = arcpy.GetParameterAsText(0)  # Workspace input
class_name = arcpy.GetParameterAsText(1)  # Class name input
output_csv = arcpy.GetParameterAsText(2)  # Output CSV file

# Set the workspace for ArcPy
arcpy.env.workspace = workspace

# Clear the CSV file if it already exists
if os.path.exists(output_csv):
    os.remove(output_csv)

# Get a list of raster datasets in the workspace
rasters = arcpy.ListRasters()

# Loop through each raster in the list
for raster in rasters:
    count_pixels_for_all_values(raster, class_name, output_csv)
