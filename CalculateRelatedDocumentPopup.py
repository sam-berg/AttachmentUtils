import arcpy

updateFields=['ID','attachpath','HAS_CS','HAS_WATER','HAS_RECLAIM','HAS_STORM','HAS_SANITARY'] #todo params
searchFields=['ID','PLAN_','CS','WATER','RECLAIM','STORM','SANITARY'] #todo params
myworkspace= r'C:\Users\sberg\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\Connection to ._sql_express.sde' #todo params

inputFeatures=None
targetDescriptionField=None
relatedTable=None
documentField=None
serverPathPrepend=None


inputFeatures = arcpy.GetParameterAsText(0)
arcpy.AddMessage("Input Features: " + inputFeatures)

targetDescriptionField = arcpy.GetParameterAsText(1)
arcpy.AddMessage("Attachment Path Field: " + targetDescriptionField)

relatedTable = arcpy.GetParameterAsText(2)
arcpy.AddMessage("Related Table: " + relatedTable)

documentField = arcpy.GetParameterAsText(3)
arcpy.AddMessage("Document Field: " + documentField)

serverPathPrepend = arcpy.GetParameterAsText(4)
arcpy.AddMessage("Server Path Prepend: " + serverPathPrepend)



iDocs=0

try:
    edit=arcpy.da.Editor(myworkspace) 
    edit.startEditing()
    edit.startOperation()

#For each centerline
    arcpy.AddMessage("Reading Input Features...")
    with arcpy.da.UpdateCursor(inputFeatures,updateFields ) as selectedInputFeatures:
        for row in selectedInputFeatures:
#	Get related records
            sourceID=str(row[0])
            where="ID=" + sourceID

            arcpy.AddMessage("searching related records for " + where)
            HAS_CS=False
            HAS_WATER=False
            HAS_RECLAIM=False
            HAS_STORM=False
            HAS_SANITARY=False
            with arcpy.da.SearchCursor(relatedTable,searchFields, where) as selectedRelatedFeatures:
            
                documentPaths="" # clear description

#		For each related record
                iDocs=0

                for row2 in selectedRelatedFeatures:
                    
#			Read document path
                    documentName=row2[1]

#           determine plan type
                    #todo test
                    if row2[2]==1:HAS_CS=True
                    if row2[3]==1:HAS_WATER=True
                    if row2[4]==1:HAS_RECLAIM=True
                    if row2[5]==1:HAS_STORM=True
                    if row2[6]==1:HAS_SANITARY=True


#			Append server path with document path
                    documentPath=serverPathPrepend + documentName
                    documentPath="<a href='" + documentPath + "'>" + documentName + "</a>" 
#			Concatenate HTML
                    documentPaths+= '</br>' + documentPath
                    iDocs+=1

#Calculate into target URL field
            documentPaths=str(iDocs) + " related document(s):</br>" + documentPaths

            row[1]=documentPaths

# update document type
            #todo test:
            if HAS_CS==True:row[2]=1
            if HAS_WATER==True:row[3]=1
            if HAS_RECLAIM==True:row[4]=1
            if HAS_STORM==True:row[5]=1
            if HAS_SANITARY==True:row[6]=1

    
            selectedInputFeatures.updateRow(row)

    edit.stopOperation()
    edit.stopEditing(True)
    arcpy.AddMessage ("Complete.")

except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
    edit.stopEditing(False)
    arcpy.AddMessage ("Finished with Error.")



