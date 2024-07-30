import sys
import datetime 
from importer.providers.poste import get_data as poste_data, resolve_data as poste_resolve_data
from importer.providers.revolut import get_data as revolut_data
from db.db import init as init_db, backup as backup_db, query, select_one, insert, select
from db.utils import find_or_create_account, add_transaction_if_not_exists


#data = poste_resolve_data('../data/poste/postepay-evolution_************5566/ListaMovimenti_PPE_Aprile_2024.pdf', 'postepay-evolution-lista-movimenti')
#data = poste_resolve_data('../data/poste/postepay-evolution_************5566/Rendiconto della Carta  Postepay Evolution Dicembre 2023.pdf', 'postepay-evolution')
#print(json.dumps(data, indent=4))
#exit()

def poste_record_to_transaction(poste_record, account_id):
    def to_float(value):
        if value == '':
            return 0
        return float(value.replace('.', '').replace(',', '.'))

    def to_timestamp(date):
        date = date.split('/')
        year = len(date[2]) == 2 and f'20{date[2]}' or date[2]
        date = f'{year}-{date[1]}-{date[0]}'
        try:
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)
            #return int(date_obj.timestamp())
            return date_obj.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError("Invalid date format.")
    
    accrediti = to_float(poste_record['accrediti'])
    addebiti = to_float(poste_record['addebiti'])

    type = 'incoming' if accrediti > 0 else 'outgoing'
    amount = accrediti if accrediti > 0 else addebiti

    return {
        'import_hash': transaction['import_hash'],
        'started_date': to_timestamp(poste_record['valuta']),
        'completed_date': to_timestamp(poste_record['data']),
        'description': poste_record['operazione'],
        'amount': amount,
        'fee': 0,
        'currency': 'EUR',
        'type': type,
        'account_id': account_id    
    }

def revolut_record_to_transaction(record, account_id):
    def to_timestamp(date):
        try:
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)
            # return int(date_obj.timestamp())
            return date_obj.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError("Invalid date format.")

    
    amount = float(record['Amount'])       
    type = 'incoming' if amount > 0 else 'outgoing'
    amount = abs(amount)

    return {
        'import_hash': transaction['import_hash'],
        'started_date': to_timestamp(record['Started Date']),
        'completed_date': to_timestamp(record['Completed Date']),
        'description': record['Description'],
        'amount': abs(float(record['Amount'])),
        'fee': float(record['Fee']),
        'currency': record['Currency'],
        'type': type,
        'account_id': account_id    
    }

'''Init db'''

if '--no-backup' not in sys.argv:
    backup_db()

init_db()

'''Import data'''
poste_data = poste_data('../data/poste')
revolut_data = revolut_data('../data/revolut')

'''Store imported data'''
imported = 0
updated = 0
for account in poste_data:
    account_id = find_or_create_account(account['name'], account['asset'])
    for transactions in account['data']:
        for transaction in transactions['data']:
            result = add_transaction_if_not_exists(poste_record_to_transaction(transaction, account_id))
            imported = imported + 1 if result == 1 else imported
            updated = updated + 1 if result == -1 else updated
print(f"Imported {imported} transactions, {updated} updated from poste")
imported = 0
updated = 0
for account in revolut_data:
    account_id = find_or_create_account('revolut')
    for transaction in account['data']:
        result = add_transaction_if_not_exists(revolut_record_to_transaction(transaction, account_id))
        imported = imported + 1 if result == 1 else imported
        updated = updated + 1 if result == -1 else updated
print(f"Imported {imported} transactions, {updated} updated from revolut")


'''ASSOCIATE CUSTOM DATA'''

custom_labels = {
    "Spliiit": "description ILIKE '%spliiit%'",
    "Telefonia": "description like '%TIM%' or description like '%RICARICA TELEFONICA POSTEMOBILE%'",
    "Commissioni Poste": "description ilike 'comm.%' OR description ilike '%commission%'",
    "Bollo Bancoposta": "description ilike '%imposta%bollo%'",
    "Tabacco": "description ilike '%mikki%' OR description ilike '%tabacc%'"
}

for label in custom_labels:
    result = query(f"UPDATE transactions SET label = '{label}' WHERE id IN (SELECT id FROM transactions WHERE ({custom_labels[label]})) AND (label is NULL OR label != '{label}');").rowcount
    print(f"Updated {result} transactions with label {label}")


'''CREATE TAGS'''
tags = ['poste', 'commissioni']
tagMap = {
    'poste': None,
    'commissioni': None
}
for tag in tags:
    exist = select_one('tags', 'id', {'name': tag})
    if not exist:
        id = insert('tags', {'name': tag})
        tagMap[tag] = id
        print(f"Tag {tag} {id} created")
    else:
        tagMap[tag] = exist[0]
        print(f"Tag {tag} {exist[0]} already exist")


'''ASSOCIATE TAGS'''
transactions = query("select id, description from transactions where (description ilike 'comm.%' OR description ilike '%commission%' OR description ilike '%imposta%bollo%') AND type = 'outgoing';").fetchall()
result = 0
for transaction in transactions:
    #check transaction is associated to a tag
    tags = query('SELECT id FROM tags t WHERE t.id IN (SELECT tag_id FROM transaction_tag WHERE transaction_id = %s)', (transaction[0],)).fetchall()
    tags = [tag[0] for tag in tags]
    
    if len(tags) > 0:
        continue
  
    for tagm in tagMap:
        if tagMap[tagm] not in tags:
            insert('transaction_tag', {
                'transaction_id': transaction[0],
                'tag_id': tagMap[tagm]
            })
    result = result + 1
    
print(f"Tag commissioni, poste associated to {result} transactions")
