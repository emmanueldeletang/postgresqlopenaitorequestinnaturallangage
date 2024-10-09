# postgresqlopenaitorequestinnaturallangage
sample code and application to generate query in postgresql langage based on natural ask of custoemrs the sample will be able to 
  Import data sample from a csv and generate embedding and store the embedding in vector columns in postgresql 
  introspect your postgresql schema to generate the sql based on your schema 
  generate a sql native langage query 
  generate a emmbedding query 
  connect to a postgreql and execute the 2 query 
  load the result in a textaera to show you 



## Features
- Vector search using Azure postgreql 
- Create embeddings using Azure OpenAI text-embedding
- Use OpenAI to generate pgsqlcode and execute the query in postgresql

## Requirements
- Tested only with Python 3.12
- Azure OpenAI account
- Azure Postgresql Felexible server account

## Setup
- Create virtual environment: python -m venv .venv
- Activate virtual ennvironment: .venv\scripts\activate
- Install required libraries: pip install -r requirements.txt
- Replace keys with your own values in example.env
- don't forget to have the model openAI one text-embbeding and one GPT ( can be 4.0 ,3.5 ) ...
- be sure the to have Configure OpenAI endpoint and key and activate te extension like explain here https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/generative-ai-azure-openai

## Demo script
- launch python import.py to import the data and create a table
- launch python app.py to launch the application go the the local webapp http://127.0.0.1:5000/

- you can enter  " give me the number of customer by country and city " generation of group by
- - you can enter give me the details of the customer in Cyprus who generate a where close 
