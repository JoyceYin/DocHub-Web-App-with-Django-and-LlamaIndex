# DocHub-Web-Application
A Full-Stack Web App with LLamaIndex and Django to query and summarize documents

### Objectives

This web application aims to manage the documents and extract the information efficiently by using Large Language Models (LLM). By uploading your resource/document, you are able to ask anything on the chatbox that combines uploaded data. In the meantime, LLM enables us to summarize each document to grab its main idea.

### Source

This web application is mainly developed by <b>Django</b> (Web Framework) and <b>LLamaIndex</b> (Data Framework for LLM Application) in Python.

### Installation and Run

Ensure to install [Ollama](https://ollama.com/) in your local and pull LLM from Ollama (Check out [LIBRARIES](https://ollama.com/library) to look for a suitable model):
```ollama
ollama pull your_model
```

Make sure to install all required libraries below:
```shell
pip install -r requirements.txt
```
Make sure to install all required libraries below:
```python
### document/views.py
### For Mac User
embed_model = LangchainEmbedding(
    HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device': 'mps'})
)
embed_model = LangchainEmbedding(
    HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
)
```

To start the project: 
```python
python manage.py runserver
```

### Demo

![test](https://github.com/JoyceYin/DocHub-Web-Application/assets/65861783/556a7f0d-a0f1-4101-aac2-a6e920a5e125)

