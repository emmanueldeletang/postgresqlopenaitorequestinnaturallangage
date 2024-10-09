import psycopg2
from openai import AzureOpenAI
import os
from dotenv import dotenv_values
import json
from flask import Flask, request, render_template, jsonify
import re


env_name = "example.env" # following example.env template change to your own .env file name
config = dotenv_values(env_name)

openai_endpoint = config['openai_endpoint']
openai_key = config['openai_key']
openai_version = config['openai_version']
openai_embeddings_model = config['openai_embeddings_deployment']
openai_chat_model = config['AZURE_OPENAI_CHAT_MODEL']

openai_client = AzureOpenAI(
  api_key = openai_key,  
  api_version = openai_version,  
  azure_endpoint =openai_endpoint 
)


# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=config['pgdbname'],
    user=config['pguser'],
    password=config['pgpassword'],
    host=config['pghost'],
    port=config['pgport']
)
cur = conn.cursor()

def generate_embeddings(openai_client, text):
    """
    Generates embeddings for a given text using the OpenAI API v1.x
    """
    
    print("Generating embeddings for: ", text, " with model: ", openai_embeddings_model)
    response = openai_client.embeddings.create(
        input = text,
        model= openai_embeddings_model
        
    )
    embeddings = response.data[0].embedding
    return embeddings


def get_table() : 
 # Query to get all table names
    tables = cur.execute("""
        SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' """)
    # Fetch all table names
    tablename = []
    tables = cur.fetchall()
    for table in tables:
        tablename.append(table[0]) 
   
    return tablename

def get_columns_name(table_name): 
    
    colname = []
    cols = cur.execute( f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
    cols = cur.fetchall()
    for col in cols : 
        colname.append(col[0])
    return colname


def get_db_info(): 
    table_dicts = []
    for tname in get_table() : 
        cname = get_columns_name(tname)
        table_dicts.append(({"table_name" : tname ,"columns_name" : cname}))
    return table_dicts

db_schema = get_db_info()
db_schema_string = "\n".join(f"Table: {table['table_name']}\nColumns : { ','.join(table['columns_name'])}" for table in db_schema)




def  ask_dbvector(vector,table):  
  
  
    cur = conn.cursor()
    if table == 'items':
        query = f"""SELECT * FROM """ + str(table) + """ ORDER BY emmbedding_ada002 <=> %s::vector LIMIT 5"""
    else :
        query = f"""SELECT * FROM """ + str(table) + """ ORDER BY docvector <=> %s::vector LIMIT 5"""
    print(table)
    cur.execute(query, (vector,))
    resutls = str(cur.fetchall())

    return resutls 



def ask_db(query): 
    cur = conn.cursor()
    cur.execute(query)
    resutls = str(cur.fetchall())
    
    return resutls   



def get_completion(openai_client, model, prompt: str):    
   
   
    print(model)
    print(openai_client)
    response = openai_client.chat.completions.create(
        model = model,
        messages =   prompt,
        temperature = 0.1
    )   
    print(response)
    
    return response.model_dump()


def generatecompletionede(user_prompt) -> str:
    
 
    system_prompt = f'''
    You are an AI assistant that is able to convert natural language into a properly formatted SQL query for PostgreSQL Server.

    SQL should be write use the following schema definition:
    '''
    system_prompt = system_prompt + db_schema_string 
    system_prompt = system_prompt + '''You must always output your answer in JSON format with the following key-value pairs:
        - "query": the SQL query that you generated
        - "error": an error message if the query is invalid, or null if the query is valid
    '''     
    

    messages = [{'role': 'system', 'content': system_prompt}]
    #user prompt
    messages.append({'role': 'user', 'content': user_prompt})

    response = get_completion(openai_client, openai_chat_model, messages)

    return response['choices'][0]['message']['content']


def extract_table_name(query):
    # Regular expression to match the table name
    match = re.search(r'FROM\s+(\w+)\s+WHERE', query, re.IGNORECASE)
    
    if match is None:
        match = re.search(r'FROM\s+(\w+)\s+GROUP', query, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    query = None
    result2 = None
    if request.method == 'POST':
        user_prompt = request.form['prompt']
        response = generatecompletionede(user_prompt)
        codePart = response.split('```json')
        json_string = codePart[1].strip().rstrip('```').rstrip()

        json_response = json.loads(json_string)
        query = json_response['query']
        table_name = extract_table_name(query)
        print(table_name)  # Output: items
        result = ask_db(query)
        table = extract_table_name(query)
        
        vector =  generate_embeddings(openai_client, user_prompt)
        result2 = ask_dbvector(vector,table)
   
      
      
    return render_template('index.html', query=query, result=result ,result2=result2 )

if __name__ == '__main__':
    app.run(debug=True)