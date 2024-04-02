#function for displaying documents before processing
from django.core.files.storage import FileSystemStorage
import os

def DocDisplay(src_loc, filelist, FileModel, valid_df, source=False):
    fs = FileSystemStorage()
    limit_list = ['pdf','doc','docx','txt']
    filemsg = []

    #save valid file and save result to json
    for file in filelist:
        newF = dict()
        newF["fname"] = file.name
        ext = file.name.split('.')[-1].lower()
        if source:
            newF['source'] = src_loc.split('/')[-1]

        if ext not in limit_list:
            newF["url"] = "N/A"
            newF["status"] = "Must be {}!".format('/'.join(limit_list))
            
        elif (FileModel.objects.filter(doc_name=file.name)):
            newF["url"] = "N/A"
            newF["status"] = "Result stored in database/Rename the doc"
        else:
            src = "Doc/"
            name = fs.save(src + file.name, file)
            doc_link = fs.url(name)
            newF["url"] = doc_link
            newF["status"] = "Ready to Process!"
            if source:
                valid_df.loc[len(valid_df.index)] = [file.name, doc_link, src_loc.split('/')[-1]]
            else:
                valid_df.loc[len(valid_df.index)] = [file.name, doc_link]
        filemsg.append(newF)

    return filemsg


def UploadInitialize(src_loc, count_df, valid_df, FileDB):
    count_df = count_df[0:0]
    count_df.to_csv(src_loc + '/upload_time.csv', index = False)
    valid_df = valid_df[0:0]
    valid_df.to_csv(src_loc + '/valid.csv', index = False)

    processFiles = [item['doc_name'] for item in list(FileDB.objects.values('doc_name'))]
    existingFiles = [i for i in os.listdir(src_loc+'Doc')]
    print(processFiles, existingFiles)

    removeFiles = [f for f in existingFiles if f not in processFiles]

    for file in removeFiles:
        os.remove(src_loc + 'Doc/' + file)