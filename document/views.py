from django.shortcuts import render
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Count
from .function import answerLLM, uploadLLM, CreateNewGroup
from .operation import DocDisplay, UploadInitialize
from .forms import UploadForm
from .models import DocInfo, SumDoc, Keyword

import pandas as pd
import os
import ast
import json

from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

from llama_index.core import ServiceContext
from llama_index.llms.ollama import Ollama
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding
import chromadb
from chromadb import Settings

llm = Ollama(model="tinyllama",  #openhermes2.5-mistral
             temperature=0.1)
embed_model = LangchainEmbedding(
    HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device': 'mps'})  #model_kwargs={'device': 'mps'}
)
sum_db = chromadb.PersistentClient(path="document/chroma_sumdb", settings=Settings(anonymized_telemetry=False) )
qa_db = chromadb.PersistentClient(path="document/chroma_qadb", settings=Settings(anonymized_telemetry=False) )

st_model = SentenceTransformer("all-MiniLM-L6-v2")
kw_model = KeyBERT(model=st_model)

# Create your views here.
def HomePage(request):
    content = {'title':'A Document WorkSpace','subtitle':'Get your references organized and knowledgable.'}
    return render(request, 'document/home.html',content)

def query(request):
    if request.method == "POST":
        print(request.POST)
        query = request.POST.get('query',None)
        result = answerLLM(query, qa_db, embed_model, llm)
        return render(request, "document/query.html", {"query":query ,"result": result})
    return render(request, "document/query.html")

def sumdb(request):
    substr = request.GET.get("q")
    if substr:
        doc_id = DocInfo.objects.filter(name__icontains=substr).values('id')
        sum_files = SumDoc.objects.filter(doc_id__in=doc_id)
    else:
        sum_files = SumDoc.objects.all()
    return render(request, "document/summarize.html", {'sum_files':sum_files})

def groupdb(request):

    if request.method == "POST":
        print(request.POST)
        if 'create' in request.POST.keys():
            newkwd = request.POST.get('create',None)
            num = request.POST.get('quantity',None)
            msg = CreateNewGroup(newkwd, qa_db, num, DocInfo, Keyword)

            kwd_list = Keyword.objects.all()
            group_kwd = list(Keyword.objects.values('kwd').annotate(cnt=Count('kwd')))
            group_kwd = json.dumps(group_kwd)
            return render(request, 'document/groupdoc.html', {'kwd_list':kwd_list, 
                                                              "group_kwd":group_kwd, 'msg':msg})
    kwd_list = Keyword.objects.all()
    group_kwd = list(Keyword.objects.values('kwd').annotate(cnt=Count('kwd')))
    group_kwd = json.dumps(group_kwd)
    return render(request, 'document/groupdoc.html', {'kwd_list':kwd_list, "group_kwd":group_kwd})

def upload(request):

    src_loc = 'media/'
    count_df = pd.read_csv(src_loc + 'upload_time.csv')
    valid_df = pd.read_csv(src_loc + 'valid.csv')
    
    if request.method == "POST":
        if len(request.FILES) == 1:
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                filelist = request.FILES.getlist('file')
                filemsg = DocDisplay(src_loc, filelist, DocInfo, valid_df)

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
                DBdict = {
                    'DocInfo': DocInfo,
                    'SumDoc': SumDoc,
                    'Keyword': Keyword
                }
                output = uploadLLM(src_loc, valid_df, qa_db, sum_db, embed_model, llm, kw_model, DBdict)
                valid_df = valid_df[0:0]
                valid_df.to_csv(src_loc + 'valid.csv', index = False)
                return render(request, 'document/upload.html', {"output":output})
        
    else:
        UploadInitialize(src_loc, count_df, valid_df, DocInfo)
        form = UploadForm()
    return render(request, "document/upload.html", {'form': form})

def manage(request):
    all_files = DocInfo.objects.all().values()
    print(all_files)
    return render(request, 'document/manage.html', {'all_files': all_files})

def delete(request, id):
    
    file = DocInfo.objects.get(id=id)
    file_row = list(DocInfo.objects.filter(id=id).values())[0]
    filename = file_row['name']
    
    #delete record from qacorpus collection
    qa_collection = qa_db.get_collection('qacorpus')
    prev = qa_collection.count()
    emd_ids = qa_collection.get(where={"file_name": filename})['ids']
    # print(emd_ids)
    qa_collection.delete(
        where={"file_name": filename}
    )
    
    now = qa_collection.count()
    print('{} item(s) removed from collection, current Count:{}, ids:{}'.\
        format(prev-now, now, emd_ids))

    #delete from db
    file.delete()

    print(SumDoc.objects.count(), Keyword.objects.count())

    os.remove('media/Doc/'+filename)
    return HttpResponseRedirect(reverse('manage'))
