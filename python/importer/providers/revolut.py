import os
import csv
import hashlib

def get_data(base_path):
    data = []
    for account_csv_path in os.listdir(base_path):
        if account_csv_path.endswith('.csv'):
            account = {}
            account_csv = os.path.join(base_path, account_csv_path)
            parts = account_csv.split('_')
            start_date = parts[1]
            end_date = parts[2]
            account['start_date'] = start_date
            account['end_date'] = end_date
            account['path'] = account_csv
            
            try:
                account['data'] = resolve_data(account_csv)
            except Exception as e:
                print(f"[ERROR] Error parsing {data['path']}: {e}")
                continue
            data.append(account)
    return data

def resolve_data(file):
    data = []
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for index, row in enumerate(reader):
            row = {key: value.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8') for key, value in row.items()}
            row['import_hash'] = hashlib.sha256(f'{str(index)}_{str(row)}'.encode()).hexdigest()
            data.append(row)

    # Type: TOPUP ricarica, CARD PAYMENT pagamento con carta,TRANSFER pagamento verso altro revolut
    # State status "COMPLETED" | "REVERTED"  | "PENDING"
    # EXCHANGE cambio valuta

    saldo = 0
    accrediti = 0
    addebiti = 0

    filtered_data = []
    for row in data:
        if row["State"] != "COMPLETED":
            # quelle con lo status pending non scalano i soldi contabili (in Balance)
            continue

        saldo = row["Balance"]
        amount = float(row["Amount"])
        if (amount < 0):
            addebiti += abs(amount)
        else:
            accrediti += amount

        fee = float(row["Fee"])
        if (fee > 0):
            addebiti += fee
        else:
            accrediti += fee
        
        filtered_data.append(row)

    differenza = round(accrediti - addebiti, 4)

    if differenza != float(saldo):
        raise Exception(f"Errore: la differenza tra accrediti e addebiti non corrisponde al saldo finale. Differenza: {differenza}, Saldo: {saldo}")

    print(f"[OK] file {file} per il provider revolut importato corretamente")


    return filtered_data

