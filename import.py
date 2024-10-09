import psycopg2
import csv
from dotenv import dotenv_values

env_name = "example.env" # following example.env template change to your own .env file name
config = dotenv_values(env_name)

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=config['pgdbname'],
    user=config['pguser'],
    password=config['pgpassword'],
    host=config['pghost'],
    port=config['pgport']
)
cur = conn.cursor()



# Create table
cur.execute('''
    CREATE TABLE IF NOT EXISTS customer (
        Index TEXT,
        Customer_Id TEXT,
        First_Name TEXT,
        Last_Name TEXT,
        Company TEXT,
        City TEXT,
        Country TEXT,
        Phone1 TEXT,
        Phone2 TEXT,
        Email TEXT,
        Subscription_Date TEXT,
        Website TEXT,
        allfields TEXT
    )
''')
conn.commit()


with conn:
    with conn.cursor() as cur:
        # Read CSV file and insert data into the table
        with open('customers100.csv', 'r') as f:
            reader = csv.reader(f, delimiter=',')
            header = next(reader)  # Skip the header row
            row_count = 0
            batch_size = 10
            batch = []

            for row in reader:
               
                try:
                    allfields = ' '.join(row[:12])  # Concatenate all fields
                    batch.append((
                        row[0],  # Categorie
                        row[1],  # Event perimeter
                        row[2],  # Event main process
                        row[3],  # Site
                        row[4],  # Standards Topics
                        row[5],  # Event Date
                        row[6],  # Numero Du Constat
                        row[7],  # Type
                        row[8],
                        row[9],
                        row[10],
                        row[11],
                        allfields  # All fields concatenated
                    ))
                    row_count += 1

                    if row_count % batch_size == 0:
                        try:
                            cur.executemany(
                                '''
                                INSERT INTO customer (Index,Customer_Id,First_Name,Last_Name,Company,City,Country,Phone1,Phone2,Email,Subscription_Date,Website, allfields
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ''', batch
                            )
                            conn.commit()
                            print(f"Committed {row_count} rows")
                        except Exception as e:
                            print(f"Error inserting batch: {e}")
                        finally:
                            batch = []

                except IndexError as e:
                    print(f"Missing index in row: {e}")
                except Exception as e:
                    print(f"Error processing row: {e}")

            # Final commit for remaining rows
            if batch:
                try:
                    cur.executemany(
                        '''
                        INSERT INTO customer (Index,Customer_Id,First_Name,Last_Name,Company,City,Country,Phone1,Phone2,Email,Subscription_Date,Website, allfields
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', batch
                    )
                    conn.commit()
                    print(f"Committed remaining {len(batch)} rows")
                except Exception as e:
                    print(f"Error inserting final batch: {e}")



cur = conn.cursor()
cur.execute('''
ALTER TABLE customer 
ADD COLUMN docvector vector(1536) -- multilingual-e5 embeddings are 384 dimensions
GENERATED ALWAYS AS (azure_openai.create_embeddings('text-embedding-ada-002', allfields)::vector) STORED; -- TEXT string sent to local model
'''
)
conn.commit()

# creation de l'index hnsw
cur = conn.cursor()
cur.execute(
                                '''
                CREATE INDEX ON customer  USING hnsw (docvector vector_ip_ops);  '''
             )
conn.commit()

#UPDATE hager_events 
#SET doc_vector = azure_openai.create_embeddings('text-embedding-ada-002', all_fields)
#where categorie = 'Lesson Learned';
#CREATE INDEX ON hager_events USING hnsw (doc_vector vector_ip_ops);

