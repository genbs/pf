
import datetime 
from importer.providers.poste import get_data as poste_data, resolve_data as poste_resolve_data
from importer.providers.revolut import get_data as revolut_data
from db.db import init as init_db
from db.utils import find_or_create_account, add_transaction_if_not_exists
import json

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
init_db()

'''Import data'''
poste_data = poste_data('../data/poste')
revolut_data = revolut_data('../data/revolut')

'''Store imported data'''
imported = 0
for account in poste_data:
    account_id = find_or_create_account(account['name'], account['asset'])
    for transactions in account['data']:
        for transaction in transactions['data']:
            imported = imported + 1 if add_transaction_if_not_exists(poste_record_to_transaction(transaction, account_id)) else imported
print(f"Imported {imported} transactions from poste")
imported = 0
for account in revolut_data:
    account_id = find_or_create_account('revolut')
    for transaction in account['data']:
        imported = imported + 1 if add_transaction_if_not_exists(revolut_record_to_transaction(transaction, account_id)) else imported
print(f"Imported {imported} transactions from revolut")

