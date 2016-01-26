
layer_name = 'Street'
attachpathfield='Attach_path'
myworkspace=None

mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]

layer_name = arcpy.GetParameterAsText(0)
arcpy.AddMessage("Centerline layer: " + layer_name)

attachpathfield=arcpy.GetParameterAsText(1)
arcpy.AddMessage("Attachment Path: " + attachpathfield)

for lyr in arcpy.mapping.ListLayers(mxd, "", df):
    if lyr.name == layer_name:
        myworkspace=lyr.workspacePath

#clear selection
arcpy.SelectLayerByAttribute_management(layer_name, 'CLEAR_SELECTION', '#')

#clear Attach_path
#with arcpy.da.Editor(myworkspace) as edit:
arcpy.CalculateField_management(layer_name, attachpathfield, '""', 'PYTHON')


