import pandas as pd
import numpy as np
from numpy.linalg import norm
from datetime import datetime 
import shutil

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
def uploadLLM(src_loc, valid_df, qa_db, sum_db, embed_model, llm, FileDB):
    message = []
    qa_collection = {}
    qa_index = {}

    sum_query = 'please summarize the document'
    sum_collection = {}
    sum_index = {}

    for _,row in valid_df.iterrows():
        newD = dict()
        newD['fname'] = row['file_name']
        newD['url'] = row['link'].replace(" ", "%20")

        filepath =  src_loc + 'Doc/' + row['file_name']

        shutil.move(filepath, src_loc + 'LLMprocess')
        path = src_loc + 'LLMprocess/'

        documents = SimpleDirectoryReader(input_dir=path, recursive=True).load_data()
        # id_ = [dict(doc)['id_'] for doc in documents]
        # print(id_)

        #summarization
        try:
            sum_db.delete_collection('summarize')
        except:
            sum_collection = sum_db.create_collection('summarize')
        sum_vector_store = ChromaVectorStore(chroma_collection=sum_collection, llm=None)
        # storage_context = StorageContext.from_defaults(vector_store=sum_vector_store)
        sum_index = VectorStoreIndex.from_documents(
            documents, embed_model=embed_model
        )
        query_engine = sum_index.as_query_engine(llm=llm)
        sum_response = query_engine.query(sum_query)

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
        sum_insert = FileDB(doc_name=newD['fname'], sum_content=newD['result'])
        # print(SumDB.objects.get(doc_name=newD['fname']).values('doc_id'))
        sum_insert.save()
        
    return message