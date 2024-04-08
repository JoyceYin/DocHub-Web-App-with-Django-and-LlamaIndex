# DocHub-Web-Application
A Full-Stack Web App with **LLamaIndex** and **Django** to query and summarize documents

### Table of Content
- [Objectives](#Objectives)
- [Set Up](#Set-Up)
- [Methodology](#Methodology)
- [Demo](#Demo)
---

### Objectives

This web application aims to manage the documents and extract the information efficiently by using Large Language Models (LLM). By uploading your resource/document, you are able to ask anything on the chatbox that combines uploaded data. In the meantime, LLM enables us to summarize each document to grab its main idea.

### Source

This web application is mainly developed by <b>Django</b> (Web Framework) and <b>LLamaIndex</b> (Data Framework for LLM Application) in Python and JavaScript (d3.js) for visualization.

### Set Up

<li>Ensure to install <a href="https://ollama.com/"><b>Ollama</b></a> in your local and pull LLM from Ollama (Check out <a href="https://ollama.com/library"><b>LIBRARIES</b></a> to look for a suitable model):</li>

```ollama
ollama pull your_model
```

<li>Make sure to install all required libraries below: </li>

```shell
# set up a new virtual env
python -m venv <myenvname>
<myenvname>/Scripts/activate
# install all required libraries
pip install -r requirements.txt
```

<li>Make sure to install all required libraries below: </li>

```python
### document/views.py
### For Mac User
embed_model = LangchainEmbedding(
    HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
            model_kwargs={'device': 'mps'})
)
embed_model = LangchainEmbedding(
    HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
)
```

<li>To start the project:</li>

```python
python manage.py runserver
```

### Methodology
#### 1. LLMs Implementation

**Ollama and LlamaIndex**

Ollama has open-source LLMs that can run locally. As an AI-language model, there is multiple language assistance, in this web app, we mainly focus on question-answering and summarizing, enabling us to read and locate sources in documents efficiently. 

LLAMA 2/LLaVA Model/

LlamaIndex is a data framework for building LLM applications, which more focus on RAG use cases compared with LangChain.

**RAG Architect**

RAG is a technique for augmenting LLM knowledge with additional data (in my case, uploaded documents), which contains two components: 1. Indexing and 2. Retrieval and Generation.

1. Indexing: Data loading -- Split into Small Chunks -- Store vector/embedding

    ```python
    documents = SimpleDirectoryReader(input_dir=path, recursive=True).load_data() #loading data and splitting
    sum_index = VectorStoreIndex.from_documents( documents, storage_context=storage_context, embed_model=embed_model) #storing vector
    ```

    ![image](https://github.com/JoyceYin/DocHub-Web-App-with-Django-and-LlamaIndex/assets/65861783/b164b8ed-d28d-4c7a-84c8-07d42cd324d0)
    Why Splitting: Text splitters break large Documents into smaller chunks. This is useful both for indexing data and for passing it into a model, since large chunks are harder to search over and won’t fit in a model’s finite context window [^1].

2. Retrieval and Generation
   
    ```python
    query="ask something..."
    query_engine = sum_index.as_query_engine(llm=llm)
    response = query_engine.query(query)
    ```

**Vector Database: ChromaDB**

To store every small chunk of document embedding, ChromaDB is employed as the vector database, which is an open-source embedding database. In ChromaDB, we could: 1)store embeddings and their metadata, 2)embed documents and queries, and 3)search embeddings.

To generate QA chat based on uploaded documents, we stored document embeddings on one ChromaDB collection to enrich document knowledge. When users post query data, it can directly search from embedded document chunks. When we look for a group of documents that related to a specific topic, we can simply query the collection by looking at the similarity. Besides, we could manage files by deleting unwanted embedding from existing collections. 

#### 2. Database Schema

#### 3. Keyword based Document Grouping

### Demo

![test](https://github.com/JoyceYin/DocHub-Web-Application/assets/65861783/556a7f0d-a0f1-4101-aac2-a6e920a5e125)

### Reference
[^1][Q&A with RAG | LangChain](https://python.langchain.com/docs/use_cases/question_answering/#rag-architecture) 
