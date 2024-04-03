import pandas as pd
import numpy as np
from datetime import datetime 
import shutil
import os

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext

#querying
def answerLLM(query, qa_db, embed_model, llm):
    chroma_collection = {}
    index = {}
    try:
        chroma_collection = qa_db.get_collection("qacorpus")
    except:
        chroma_collection = qa_db.create_collection("qacorpus")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection, llm=None)
    # print(chroma_collection.get('2013_2.txt', include=['ids']))
    
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)
    
    query_engine = index.as_query_engine(llm=llm)
    response = query_engine.query(query)
    
    return str(response)

#upload files: summarizing + add RAG for qa
def uploadLLM(src_loc, valid_df, qa_db, sum_db, embed_model, llm, kw_model, DBdict):
    message = []
    qa_collection = {}

    sum_query = 'please summarize the document'
    sum_collection = {}
    sum_index = {}

    #not suitable for tinyllama
    # kwd_query = 'Please list 3 main keywords of this document and seperated by comma.'

    for _,row in valid_df.iterrows():
        newD = dict()
        newD['fname'] = row['file_name']
        newD['url'] = row['link'].replace(" ", "%20")

        filepath =  src_loc + 'Doc/' + row['file_name']

        #clear LLMprocess folder
        for file in os.listdir(src_loc + 'LLMprocess'):
            os.remove('media/LLMprocess/'+file)

        shutil.move(filepath, src_loc + 'LLMprocess')
        path = src_loc + 'LLMprocess/'

        documents = SimpleDirectoryReader(input_dir=path, recursive=True).load_data()
        text_ = '/n'.join([dict(doc)['text'] for doc in documents])
        
        keywords = kw_model.extract_keywords(text_, keyphrase_ngram_range=(1, 2), 
                                             stop_words='english', threshold=.75, 
                                             use_mmr=True, top_n=3)

        newD['keyword'] = [k[0] for k in keywords]

        #summarization
        # try:
        #     sum_db.delete_collection('summarize')
        # except:
        #     sum_collection = sum_db.create_collection('summarize')
        # sum_vector_store = ChromaVectorStore(chroma_collection=sum_collection, llm=None)

        # storage_context = StorageContext.from_defaults(vector_store=sum_vector_store)
        sum_index = VectorStoreIndex.from_documents(
            documents, embed_model=embed_model
        )

        query_engine = sum_index.as_query_engine(llm=llm)
        sum_response = query_engine.query(sum_query)

        # kwd_response = query_engine.query(kwd_query)
        # newD['keyword'] = kwd_response
        # keywords = kw_model.extract_keywords(documents)

        if len(str(sum_response)) == 0:
            newD['status'] = 'Skip'
            newD['result'] = 'N/A'
        else:
            newD['status'] = 'Finish'
            newD['result'] = str(sum_response)

        #qa
        qa_collection = qa_db.get_or_create_collection('qacorpus')
        
        qa_vector_store = ChromaVectorStore(chroma_collection=qa_collection, llm=None)
        storage_context = StorageContext.from_defaults(vector_store=qa_vector_store)
        qa_index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context, embed_model=embed_model
        )
        
        print('collection item count:', qa_collection.count())
        newD['qastatus'] = 'Add {} items into chromaDB Collection'.\
            format(len(qa_collection.get(where={"file_name": newD['fname']})['ids']))
            
        shutil.move(path + row['file_name'], src_loc + 'Doc') 

        message.append(newD)

        ##save to database
        doc_insert = DBdict['DocInfo'](name=newD['fname'],url=newD['url'])
        doc_insert.save()

        sum_insert = DBdict['SumDoc'](doc_id=DBdict['DocInfo'].objects.get(name=newD['fname']),
                                      sum_content=newD['result'])
        sum_insert.save()

        for k in newD['keyword']:
            kwd_insert = DBdict['Keyword'](doc_id=DBdict['DocInfo'].objects.get(name=newD['fname']),
                                            kwd=k)
            kwd_insert.save()
        
    return message

def CreateNewGroup(newkwd, qa_db, num, DocInfo, Keyword):
    try:
        collection = qa_db.get_collection('qacorpus')
        if DocInfo.objects.count() == 0:
            return 'no document uploaded'
        else:
            checked = list(Keyword.objects.filter(kwd=newkwd).values())
            ### make sure not duplicated keyword
            if len(checked) == 0:
                results = collection.query(
                    query_texts=[newkwd],
                    n_results= int(num)
                )
                results = results['metadatas'][0]
                doc_list = list(set([k['file_name'] for k in results]))
                ##save to DB
                for doc in doc_list:
                    kwd_insert = Keyword(doc_id=DocInfo.objects.get(name=doc), 
                                        kwd=newkwd)
                    kwd_insert.save()
                return 'Add {} Group successfully!'.format(newkwd)
            else:
                return '{} Group existed'.format(newkwd)
    except:
        return 'no document uploaded'
