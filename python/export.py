
from db.db import init as init_db, select
from db.utils import find_or_create_account, add_transaction_if_not_exists

init_db()

data = select('transactions_view', 'id, started, completed, description, amount, fee, currency, type, account')
csv = 'id,started,completed,description,amount,fee,currency,type,account\n'
for row in data:
    csv = csv + f'"{row[0]}","{row[1]}","{row[2]}","{row[3]}",{row[4]},{row[5]},"{row[6]}","{row[7]}","{row[8]}"\n'

# store csv to file
with open('../transactions.csv', 'w') as file:
    file.write(csv)
    file.close()
    print(f"Data exported to ../transactions.csv")
               
