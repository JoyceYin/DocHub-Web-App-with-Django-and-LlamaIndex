from django.shortcuts import render
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .function import answerLLM, uploadLLM
from .operation import DocDisplay, UploadInitialize
from .forms import UploadForm
from .models import SumDB, queryDB

import pandas as pd
import os
import ast

from llama_index.core import ServiceContext
from llama_index.llms.ollama import Ollama
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding
import chromadb
from chromadb import Settings

llm = Ollama(model="openhermes2.5-mistral",  #openhermes2.5-mistral 
             temperature=0.1)
embed_model = LangchainEmbedding(
    HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')  #model_kwargs={'device': 'mps'}
)
sum_db = chromadb.PersistentClient(path="document/chroma_sumdb", settings=Settings(anonymized_telemetry=False) )
qa_db = chromadb.PersistentClient(path="document/chroma_qadb", settings=Settings(anonymized_telemetry=False) )

# Create your views here.
def HomePage(request):
    content = {'title':'A Document WorkSpace','subtitle':'Get your references organized and knowledgable.'}
    return render(request, 'document/home.html',content)

def query(request):
    if request.method == "POST":
        print(request.POST)
        query = request.POST.get('query',None)
        result = answerLLM(query, qa_db, embed_model, llm)
        return render(request, "function/qa.html", {"query":query ,"result": result})
    return render(request, "document/query.html")

def sumdb(request):
    substr = request.GET.get("q")
    if substr:
        sum_files = SumDB.objects.filter(doc_name__icontains=substr).values()
    else:
        sum_files = SumDB.objects.all().values()
    for file in sum_files:
        file['doc_link'] = '/Doc/{}'.format(file['doc_name'])
    return render(request, "document/summarize.html", {'sum_files':sum_files})

def groupdb(request):
    return render(request, 'document/groupdoc.html')

def upload(request):

    src_loc = 'media/'
    count_df = pd.read_csv(src_loc + 'upload_time.csv')
    valid_df = pd.read_csv(src_loc + 'valid.csv')
    
    if request.method == "POST":
        if len(request.FILES) == 1:
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                filelist = request.FILES.getlist('file')
                filemsg = DocDisplay(src_loc, filelist, SumDB, valid_df)

                count_df.loc[len(count_df.index)] = [1, filemsg]
                count_df.to_csv(src_loc + 'upload_time.csv', index = False)
                valid_df.to_csv(src_loc + 'valid.csv', index = False)
                
            filemsg = []
            for l in count_df['file_list'].tolist():
                if type(l)==str:
                    l = ast.literal_eval(l)
                filemsg += l

            return render(request, "document/upload.html", {'filemsg':filemsg, 'form':form})
        else: 
            count_df = count_df[0:0]
            count_df.to_csv(src_loc + 'upload_time.csv', index = False)

            # press process button, and run
            if len(valid_df) == 0:
                urlmsg = 'There are not valid documents to process. Please press RESET to reupload documents :)'
                return render(request, 'document/upload.html', {'urlmsg':urlmsg})
            
            else:
                #run add qa and summarize
                output = uploadLLM(src_loc, valid_df, qa_db, sum_db, embed_model, llm, SumDB, queryDB)
                valid_df = valid_df[0:0]
                valid_df.to_csv(src_loc + 'valid.csv', index = False)
                return render(request, 'document/upload.html', {"output":output})
        
    else:
        UploadInitialize(src_loc, count_df, valid_df, SumDB)
        form = UploadForm()
    return render(request, "document/upload.html", {'form': form})

def manage(request):
    all_files = SumDB.objects.all().values()
    return render(request, 'document/manage.html', {'all_files': all_files})

def delete(request, id):
    #delete record from qacorpus collection
    qa_collection = qa_db.get_collection('qacorpus')
    qa_collection.delete(ids=list(queryDB.objects.filter(doc_id=id).values('id')))

    file = SumDB.objects.get(doc_id=id)
    file_row = list(SumDB.objects.filter(doc_id=id).values())[0]
    filename = file_row['doc_name']

    print(queryDB.objects.get(doc_id=id))
    qa_file = queryDB.objects.get(doc_id=id)
    qa_file.delete()

    os.remove('media/Doc/'+filename)
    file.delete()

    return HttpResponseRedirect(reverse('manage'))
