import arcpy

def rows_as_dicts(cursor):
    colnames = cursor.fields
    for row in cursor:
        yield dict(zip(colnames, row))

layer_name = 'Boston_Streets2'
inputfile= "c://atemp//VHB_logo.png"
attachpath = inputfile
attachfile='VHB_logo.png'
layer_idfield = 'OBJECTID'
pivottable_name='PIVOT'
scantable_name='scans'
attachmetadatatable_name = 'scanmetadata'
inputmxd="C://data//BostonFiber//BostonFiber.mxd"
useEditSession=False
useEditOperations=True

myworkspace = None

if(arcpy.GetParameterAsText(0)!=''):
    layer_name = arcpy.GetParameterAsText(0)

arcpy.AddMessage("Input layer: " + layer_name)

if(arcpy.GetParameterAsText(1)!=''):
    layer_idfield = arcpy.GetParameterAsText(1)
arcpy.AddMessage("Layer ID Field: " + layer_idfield)

if(arcpy.GetParameterAsText(2)!=''):
    inputfile = arcpy.GetParameter(2)
desc = arcpy.Describe(inputfile)
attachpath = str(desc.catalogPath)
arcpy.AddMessage("Attachment Path: " + attachpath)
attachfile= str(desc.file) 
arcpy.AddMessage("Attachment File: " + attachfile)

myattachfilebinary=open(attachpath,'rb').read()

if(arcpy.GetParameterAsText(3)!=''):
    pivottable_name = arcpy.GetParameterAsText(3)
arcpy.AddMessage("Pivot table: " + pivottable_name)

if(arcpy.GetParameterAsText(4)!=''):
    scantable_name = arcpy.GetParameterAsText(4)
arcpy.AddMessage("Scan table: " + scantable_name)

if(arcpy.GetParameterAsText(5)!=''):
    attachmetadatatable_name = arcpy.GetParameterAsText(5)
arcpy.AddMessage("Related Attachment Metadata Table: " + attachmetadatatable_name)


if(len(inputmxd)==0):
    mxd = arcpy.mapping.MapDocument("CURRENT")
else:
    mxd=arcpy.mapping.MapDocument(inputmxd)

df = arcpy.mapping.ListDataFrames(mxd)[0]

for lyr in arcpy.mapping.ListLayers(mxd, "", df):
    if lyr.name == layer_name:
        if myworkspace==None: myworkspace = lyr.workspacePath

arcpy.AddMessage("workpace: " + myworkspace)

arcpy.env.workspace = myworkspace #set workspace

try:

    #for each selected feature in layer
    bWeStartedEditing=False
    if useEditSession or useEditOperations: edit=arcpy.da.Editor(myworkspace) 
    if(edit.isEditing != True):
        arcpy.AddMessage("Edit Session was not found")
        useEditSession=True
        bWeStartedEditing=True
        arcpy.AddMessage("We will start editing.")

    if useEditSession: edit.startEditing(False,True)



    with arcpy.da.SearchCursor(layer_name , (layer_idfield,)) as selectedstreetcursor:
        for row in selectedstreetcursor:
            centerlineID=str(row[0])
            arcpy.AddMessage("processing feature " + centerlineID)

            fields = ['REL_OBJECTID','ATT_NAME']

            #add MULTIPLE pivot records if necessary

            if useEditOperations: edit.startOperation()
        
            with arcpy.da.InsertCursor(pivottable_name,fields ) as pivotcursor:
        
                arcpy.AddMessage("Inserting PIVOT Row...") 
                pivotcursor.insertRow((centerlineID,attachfile))
                arcpy.AddMessage("new pivot record created.")

            if useEditOperations: edit.stopOperation()
            del pivotcursor

    where ="ATT_NAME='" + attachfile + "'"
    arcpy.AddMessage(where)

    scursor2 = arcpy.da.SearchCursor(scantable_name, "ATT_NAME", where)
    bFound2=False
    for row in scursor2:
        bFound2=True
        break
    del scursor2

    #add SINGLE scan record  
    if bFound2!=True:      
        if useEditOperations: edit.startOperation()
        scanfields=['ATT_NAME','CONTENT_TYPE','DATA','DATA_SIZE']
        with arcpy.da.InsertCursor(scantable_name,scanfields) as scancursor:
        
            arcpy.AddMessage("Inserting Scan Row...") 
            scancursor.insertRow((attachfile,'image/tiff',myattachfilebinary,len(myattachfilebinary)))
            arcpy.AddMessage("new scan record created.")

        if useEditOperations: edit.stopOperation()
        del scancursor
    else:
        arcpy.AddMessage("Scan record exists for " + attachfile)    

    ##add record to metadata table if necessary

    scursor = arcpy.da.SearchCursor(attachmetadatatable_name, "ATT_NAME", where)
    bFound=False
    for row in scursor:
        bFound=True
        break
    del scursor

    if bFound != True:
        if useEditOperations: edit.startOperation()
        scanmetafields=['ATT_NAME']
        with arcpy.da.InsertCursor(attachmetadatatable_name,scanmetafields) as scanmetacursor:
        
            arcpy.AddMessage("Inserting Scan Metadata Row (ATT_NAME)...") 
            scanmetacursor.insertRow([attachfile])
            arcpy.AddMessage("new scan metadata record created.")

        if useEditOperations: edit.stopOperation()
        del scanmetacursor
    else:
        arcpy.AddMessage("Scan Metadata record exists for " + attachfile)    

    if useEditSession and bWeStartedEditing: arcpy.AddMessage("We Started Editing so stopEditing(True)")
    if useEditSession and bWeStartedEditing: edit.stopEditing(True)
    



except Exception as e :
    arcpy.AddError(e)
    if useEditSession: edit.stopEditing(False)
    
