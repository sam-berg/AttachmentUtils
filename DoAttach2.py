import arcpy

def rows_as_dicts(cursor):
    colnames = cursor.fields
    for row in cursor:
        yield dict(zip(colnames, row))

layer_name = 'lines'
attachpathvalue = r'"C:\atemp\VHB_logo.png"'
attachpathfield = 'attachpath'
layer_idfield = 'ID'
attachmetadatatable_name = 'AttachmentMetadata'
cs = None
water = None
reclaim = None
storm = None
sanitary = None

myworkspace = None
#myworkspace='C:\Users\sberg\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\._SQL_EXPRESS.gds\DelandTest (VERSION:dbo.DEFAULT)'

layer_name = arcpy.GetParameterAsText(0)
arcpy.AddMessage("Centerline layer: " + layer_name)

attachpathfield = arcpy.GetParameterAsText(1)
arcpy.AddMessage("Attachment Path Field: " + attachpathfield)

layer_idfield = arcpy.GetParameterAsText(2)
arcpy.AddMessage("Centerline ID Field: " + layer_idfield)

inputfile = arcpy.GetParameter(3)
desc = arcpy.Describe(inputfile)
attachpathvalue = str(desc.catalogPath)
attachpathvalue = '"' + attachpathvalue + '"'
arcpy.AddMessage("Attachment Path Value: " + attachpathvalue)

attachmetadatatable_name = arcpy.GetParameterAsText(4)
arcpy.AddMessage("Related Attachment Inventory Table: " + attachmetadatatable_name)

plan = arcpy.GetParameterAsText(5)
arcpy.AddMessage("plan: " + plan)

drawer = arcpy.GetParameterAsText(6)
arcpy.AddMessage("drawer: " + drawer)

cs = arcpy.GetParameterAsText(7)
arcpy.AddMessage("cs: " + cs)

water = arcpy.GetParameterAsText(8)
arcpy.AddMessage("water: " + water)

reclaim = arcpy.GetParameterAsText(9)
arcpy.AddMessage("reclaim: " + reclaim)

storm = arcpy.GetParameterAsText(10)
arcpy.AddMessage("storm " + storm)

sanitary = arcpy.GetParameterAsText(11)
arcpy.AddMessage("sanitary: " + sanitary)

mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]

for lyr in arcpy.mapping.ListLayers(mxd, "", df):
    if lyr.name == layer_name:
        if myworkspace==None: myworkspace = lyr.workspacePath

#calculate attachpath
arcpy.AddMessage("workpace: " + myworkspace)

arcpy.env.workspace = myworkspace #set workspace

edit=arcpy.da.Editor(myworkspace) 
edit.startEditing(False,True)
edit.startOperation()
arcpy.CalculateField_management(layer_name, attachpathfield, attachpathvalue, 'VB',"#")
edit.stopOperation()
edit.stopEditing(True)

#run add attachments
arcpy.AddAttachments_management(layer_name, 'OBJECTID', layer_name, 'OBJECTID', attachpathfield, '#')


count = 0
updatedcount=0
addedcount=0

try:
    edit.startEditing(True,True)
    with arcpy.da.SearchCursor(layer_name , (layer_idfield,)) as selectedstreetcursor:
        for row in selectedstreetcursor:
  
            centerlineID=str(row[0])
            arcpy.AddMessage("processing centerline " + centerlineID)

            # Search inventory table for existing empty table
            where = "ID=" + str(row[0]) + " AND (PLAN_ IS NULL OR PLAN_ = '') AND (DRAWER IS NULL OR DRAWER='')"
            attachmentmedata_recordupdate = None

           
            bIsUpdate=False
            arcpy.AddMessage("searching for " + where)
            fields = ['PLAN_', 'DRAWER','CS','WATER','RECLAIM','STORM','SANITARY']

            edit.startOperation()
            with arcpy.da.UpdateCursor(attachmetadatatable_name,fields,where ) as selectedscancursor:
                for row2 in selectedscancursor:

                    #use existing scan record if it exits, otherwise create new row
                    attachmentmedata_recordupdate=row2
                    arcpy.AddMessage("found existing blank record to update.")
                    bIsUpdate=True

                    row2[0]= plan
                    row2[1]= drawer
                    row2[2] =cs
                    row2[3]=water
                    row2[4] = reclaim
                    row2[5] = storm
                    row2[6] = sanitary

                    
                    selectedscancursor.updateRow(row2)
                    
                    updatedcount=updatedcount+1
                    arcpy.AddMessage("Updating Row...")
            edit.stopOperation()

            if bIsUpdate==False:

                edit.startOperation()
                # Create insert cursor for inventory table
                # 
                fields2 = ['ID','PLAN_', 'DRAWER','CS','WATER','RECLAIM','STORM','SANITARY']
                with arcpy.da.InsertCursor(attachmetadatatable_name,fields2) as attachmentmetadata_rows:

                    bIsUpdate=False
                
                    arcpy.AddMessage("Inserting Row...") 
                    attachmentmetadata_rows.insertRow((row[0],plan,drawer,cs,water,reclaim,storm,sanitary))
                    arcpy.AddMessage("new scan record created.")

                edit.stopOperation()
                addedcount=addedcount+1



            count = count + 1     

    edit.stopEditing(True)

    # Delete cursor and row objects to remove locks on the data
    #
    del row
  
    if bIsUpdate==True:
        if attachmentmedata_recordupdate != None: del attachmentmedata_recordupdate
        if row2!= None: del row2 




except arcpy.ExecuteError:
    print "error"
    print(arcpy.    GetMessages(2))


print "Added " + str(count) + " new records to " + attachmetadatatable_name + "..."
arcpy.AddMessage("Added (" + str(addedcount) + ") or updated (" + str(updatedcount) + ") " + str(count) + " records from " + attachmetadatatable_name + "...")




