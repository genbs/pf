from scipy.linalg import triu
from gensim import corpora

from python.db.db import init as init_db, select
from db.utils import find_or_create_account, add_transaction_if_not_exists
import pandas as pd
import ollama 
import json
import nltk
import pprint
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from gensim.models import LdaModel
nltk.download('stopwords')

init_db('../store.db')

def create_model(name='llama3/pf'):
    # check in ollama if model exists
    list = ollama.list()

    for model in list['models']:
        if model['name'] == name + ':latest':
            print(f"Model {name} already exists")
            return
        
    modelfile=f'''
FROM llama3
PARAMETER temperature 0.8
SYSTEM """
Tu sei un assistente virtuale che aiuta a gestire le finanze personali. Un professionista che ti aiuta a capire come spendi i tuoi soldi e a risparmiare. Un amico che ti aiuta a prendere decisioni finanziarie intelligenti.
"""
'''
    print(modelfile)
    ollama.create(model=name, modelfile=modelfile)
    print(f"Model {name} created")

#ollama.delete('llama3/pf')
#create_model()

data = select('transactions_view', 'id, started, completed, description, notes, amount, fee, currency, type, account')
csv = 'id,started,completed,description,notes,amount,fee,currency,type,account\n'
df_data = []
for row in data:
    csv = csv + f"{row[0]},{row[1]},{row[2]},{row[3]},,{row[4]},0.0,{row[6]},{row[7]},{row[8]},{row[9]}\n"
    df_data.append({
        'id': row[0],
        'started': row[1],
        'completed': row[2],
        'description': row[3],
        'notes': row[4],
        'amount': row[5],
        'fee': row[6],
        'currency': row[7],
        'type': row[8],
        'account': row[9]
    })

# df = pd.DataFrame(df_data, columns=['id', 'started', 'completed', 'description', 'notes', 'amount', 'fee', 'currency', 'type', 'account'])
# print(df.head()) 
# nltk.download('punkt')
# stemmer = nltk.stem.PorterStemmer()

# def extract_categories(df):
#     categories = set()
#     for desc in df['description']:
#         tokens = nltk.word_tokenize(desc)
#         stemmed_tokens = [stemmer.stem(token) for token in tokens]
#         category = ' '.join(stemmed_tokens)
#         categories.add(category.lower())

#     return list(categories)

# categories = extract_categories(df)
# print(categories) 

# # Add the category column
# df['category'] = df.apply(lambda row: ' '.join([stemmer.stem(token) for token in nltk.word_tokenize(row['description'])]).lower(), axis=1)

# grouped_df = df.groupby('category')
# print(grouped_df.size())

# for category, group_df in grouped_df:
#     print(f"Category: {category}")
#     #print(group_df.head(5))  # Print top N transactions
#     # print all transactions of the category
#     for index, row in group_df.iterrows():
#         print(f"  {row['description']} - {row['amount']} {row['currency']}")
#     print()


df = pd.DataFrame(df_data, columns=['id', 'started', 'completed', 'description', 'notes', 'amount', 'fee', 'currency', 'type', 'account'])
descriptions = df['description']
# Data preprocessing

# stop_words = set(
#     stopwords.words('english') + stopwords.words('italian')
# )
# cleaned_descriptions = []
# for desc in descriptions:
#     tokens = [token for token in desc.lower().split() if token not in stop_words]
#     cleaned_descriptions.append(' '.join(tokens))

stoplist = set(
    stopwords.words('english') + stopwords.words('italian')
)
# Lowercase each document, split it by white space and filter out stopwords
texts = [[word for word in document.lower().split() if word not in stoplist]
         for document in descriptions]

from collections import defaultdict
frequency = defaultdict(int)
for text in texts:
    for token in text:
        frequency[token] += 1

processed_corpus = [[token for token in text if frequency[token] > 1] for text in texts]
dictionary = corpora.Dictionary(processed_corpus)
print(dictionary)

doc_term_matrix = [dictionary.doc2bow(doc) for doc in processed_corpus]

# Number of topics
num_topics = 5  # Adjust this based on your needs

# Create LDA model
lda_model = LdaModel(doc_term_matrix, num_topics=num_topics, id2word=dictionary, passes=15)

# Print topics
for idx, topic in lda_model.print_topics(-1):
    print("Topic: {} \nWords: {}".format(idx, topic))

# Assign topics to documents
doc_topics = lda_model[doc_term_matrix]

# Create a DataFrame with topics
topic_df = pd.DataFrame(doc_topics)
df['topic'] = topic_df.idxmax(axis=1)

topic_to_category = {
    0: "Alimentari",  # Assuming topic 0 represents "Food"
    1: "Trasporti",  # Assuming topic 1 represents "Transportation"
    2: "Abitazione",  # Assuming topic 2 represents "Housing"
    3: "Intrattenimento",  # Assuming topic 3 represents "Entertainment"
    4: "Altro",  # Assuming topic 4 represents "Other"
}

# Assign categories to transactions
df['category'] = df['topic'].apply(lambda x: topic_to_category[x])
df['month'] = pd.to_datetime(df['started']).dt.to_period('M')
monthly_expenses = df.groupby(['month', 'category'])['amount'].sum().unstack()

# Print monthly expense report
print("Monthly Expense Report:")
print(monthly_expenses.to_string())

# # Topic modeling - Latent Dirichlet Allocation (LDA)
# num_topics = 5  # Choose an appropriate number of topics
# lda_model = LdaModel(bow_matrix, num_topics=num_topics)

# # Category generation
# predicted_topics = lda_model.predict(bow_matrix)
# data['category'] = predicted_topics
# print('predicted_topics', predicted_topics)

# # Model training - Naive Bayes classifier
# categories = data['category']
# classifier = MultinomialNB()
# classifier.fit(bow_matrix, categories)

# # Category prediction for new descriptions
# new_descriptions = ['New description 1', 'New description 2']
# new_bow_matrix = vectorizer.transform(new_descriptions)
# predicted_categories = classifier.predict(new_bow_matrix)

# # Monthly expense tracking
# monthly_expenses = data.groupby(['month', 'category'])['amount'].sum().unstack()

# print(monthly_expenses)
exit()

stream = ollama.chat(
     model='llama3',
     messages=[{'role': 'user', 'content': '''
 Lo schema del database è:
 - accounts (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     name VARCHAR NOT NULL UNIQUE,
     reference VARCHAR NULL
 )
 - transactions (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     started_date TIMESTAMP,
     completed_date TIMESTAMP,
     description TEXT,
     amount REAL,
     fee REAL,
     currency VARCHAR,
     type VARCHAR CHECK(type IN ('incoming', 'outgoing')),
     account_id INTEGER,
     FOREIGN KEY (account_id) REFERENCES accounts (id)
 )

I dati sono CSV:
            
{csv}
               
'''}],
     stream=True,
 )


for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)


