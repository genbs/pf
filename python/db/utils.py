from db.db import  insert, select_one, insert, update, query

def find_or_create_account(name, reference = None):
    account = select_one('accounts', 'id', {'name': name})
    if account:
        return account[0]
    else:
        return insert('accounts', {'name': name, 'reference': reference})
    
'''return 1 if imported, -1 if updated, 0 if nothing'''
def add_transaction_if_not_exists(transaction):
    finded = select_one('transactions', 'id, notes, label, category_id', {
        'import_hash': transaction['import_hash']
    })

    if not finded:
        insert('transactions', transaction)
        return 1
    # TODO: update note, categories, tags 
    else:
        # transaction already exists
        return 0
        tags = query('SELECT id FROM tags t WHERE t.id IN (SELECT tag_id FROM transaction_tag WHERE transaction_id = %s)', (finded[0],)).fetchall()
        
        if finded[1] or finded[2] or finded[3]:
            to_update = {
                "notes": finded[1],
                "label": finded[2],
                "category_id": finded[3]
            }

            # update if to_update is not empty
            update('transactions', to_update, f'id = {finded[0]}')
            # update categories
            # update tags

            if len(tags) > 0:
                # update tags
                pass
            else:
                return -1
        
        if len(tags) > 0:
            # update tags in db
            for tag in tags:
                insert('transaction_tag', {
                    'transaction_id': finded[0],
                    'tag_id': tag[0]
                })
                        
            
    return 0
