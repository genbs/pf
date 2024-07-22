from db.db import  insert, select_one, insert, update

def find_or_create_account(name, reference = None):
    account = select_one('accounts', 'id', {'name': name})
    if account:
        return account[0]
    else:
        return insert('accounts', {'name': name, 'reference': reference})
    
def add_transaction_if_not_exists(transaction):
    finded = select_one('transactions', 'id, notes', {
        'import_hash': transaction['import_hash']
    })

    if not finded:
        insert('transactions', transaction)
        return True
    # TODO: update note, categories, tags 
    else:
        to_update = {
            "notes": finded[1]
        }
        update('transactions', to_update, f'id = {finded[0]}')
        # update categories
        # update tags
    return False
