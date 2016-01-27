import arcpy

myworkspace= r'C:\data\BostonFiber\BostonFiber2\BostonFiber2.gdb'

inputFeatures='Boston_Streets'
targetDescriptionField='HTMLDESC'
pivottable='PIVOT'
attachtable='scans__ATTACH'

scansurl='http://gistest.vhb.com/arcgis/rest/services/BostonFiber/BostonFiberPub/MapServer/2'
attachmenttableurl='http://'
metadataurl='http://'


try:
    
    arcpy.env.workspace = myworkspace #set workspace

    edit=arcpy.da.Editor(myworkspace) 
    edit.startEditing()
    
#for each street
    updateFields=['OBJECTID',targetDescriptionField]
    with arcpy.da.UpdateCursor(inputFeatures,updateFields ) as selectedInputFeatures:
        for row in selectedInputFeatures:

            oid=row[0]
            arcpy.AddMessage("processing feature " + str(oid) )

    #init list of scans
            sDesc=''
            iDocs=0
    #get ATT_NAMEs from PIVOT

            where='REL_OBJECTID = ' + str(oid)

    #get attachment feature using query and calculate URL
            with arcpy.da.SearchCursor(pivottable,['REL_OBJECTID','ATT_NAME'],where) as pivotCursor:
                arcpy.AddMessage(where)
                for rowPivot in pivotCursor:

                    where2="ATT_NAME='" + rowPivot[1] + "'"
                    with arcpy.da.SearchCursor(attachtable,['ATTACHMENTID','REL_OBJECTID','ATT_NAME'],where2) as attachCursor:
                        arcpy.AddMessage(where2)
                        for rowAttach in attachCursor:
                            aid=rowAttach[0]
                            #arcpy.AddMessage(aid)
                            attname=rowAttach[2]
                            #arcpy.AddMessage(attname)
                            attachURL=scansurl + '/' + str(rowAttach[1]) + '/attachments/' + str(aid)
                            #arcpy.AddMessage(attachURL)
                            sDesc=sDesc +  "<a href='" + attachURL + "' />" + attname  + "</a></br>"
                            
                            iDocs=iDocs+1
                            #arcpy.AddMessage(iDocs)

    #calculate local street description field
                sDesc=str(iDocs) + " related document(s):</br>" + sDesc

                if iDocs>0:
                    row[1]=sDesc
                    arcpy.AddMessage(sDesc)
                    edit.startOperation()
                    selectedInputFeatures.updateRow(row)
                    edit.stopOperation()
    
    edit.stopEditing(True)
    if selectedInputFeatures: del selectedInputFeatures
    if attachCursor: del attachCursor
    if pivotCursor:del pivotCursor

    arcpy.AddMessage ("Complete.")

except arcpy.ExecuteError:
    arcpy.AddMessage ("Finished with Error.")
    print(arcpy.GetMessages(2))
    edit.stopEditing(True)
    
