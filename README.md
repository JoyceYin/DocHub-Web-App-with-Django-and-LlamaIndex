# DocHub-Web-Application
A Full-Stack Web App with LLamaIndex and Django to query and summarize documents

### Objectives

This web application aims to manage the documents and extract the information efficiently by using Large Language Models (LLM). By uploading your resource/document, you are able to ask anything on the chatbox that combines uploaded data. In the meantime, LLM enables us to summarize each document to grab its main idea.

### Source

This web application is mainly developed by <b>Django</b> (Web Framework) and <b>LLamaIndex</b> (Data Framework for LLM Application) in Python and JavaScript (d3.js) for visualization.

### Installation and Run

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
> [!NOTE]
> Create file storage directory "<b>Doc</b>" and LLM process directory "<b>LLMprocess</b>" under media folde

<hr>
<li>To start the project:</li>

```python
python manage.py runserver
```

### Demo

![test](https://github.com/JoyceYin/DocHub-Web-Application/assets/65861783/556a7f0d-a0f1-4101-aac2-a6e920a5e125)

