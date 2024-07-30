import os
import hashlib
from importer.pdf import parse_pdf

def get_data(base_path):
    providers = []
    for provider_dir_name in os.listdir(base_path):
        if os.path.isdir(os.path.join(base_path, provider_dir_name)):
            provider = {}
            provider_name, provider_asset = provider_dir_name.split('_')
            
            provider['name'] = provider_name
            provider['asset'] = provider_asset
            provider['data'] = []

            for file in os.listdir(os.path.join(base_path, provider_dir_name)):
                if file.endswith('.pdf'):
                    data = {}

                    provider_name_r = provider_name 

                    if file.startswith('ListaMovimenti'):
                        #print(f"[INFO] Skipping {file}")
                        #continue
                        # ListaMovimenti_PPE_Aprile_2024.pdf
                        _, _, month, year = file[:-4].split('_')
                        data['month'] = month
                        data['year'] = year
                        provider_name_r = 'postepay-evolution-lista-movimenti'
                    else:
                        month, year = file[:-4].split(' ')[-2:]
                        
                        data['month'] = month
                        data['year'] = year
                    
                    data['path'] = os.path.join(base_path, provider_dir_name, file)
                    
                    try:
                        data['data'] = resolve_data(data['path'], provider_name_r)
                    except Exception as e:
                        print(f"[ERROR] Error parsing ({provider_name_r}) {data['path']}: {e}")
                        continue

                    provider['data'].append(data)
                
            providers.append(provider)

    return providers



def resolve_data(file, provider_name): 
    data = None
    if provider_name == 'bancoposta':
        data = parse_pdf(
            path=file, 
            columns= {
                "data": [70, 75],
                "valuta": [120, 125],
                "addebiti": [210, 230],
                "accrediti": [300, 320],
                "operazione": [360, 600]
            }, 
            interesting_area=[0,100,-1,800],
            first_page_interesting_area=[0,300,-1,800],
            required_columns=['data', 'operazione'],
            possible_multiple_rows=['operazione'],
            stop_fn=lambda value, values: value['operazione'] == 'SALDO FINALE'
        )
    elif provider_name == 'postepay-evolution': # rendiconto
        data = parse_pdf(
            path=file, 
            columns={
                "data": [80, 100],
                "valuta": [140, 160],
                "addebiti": [220, 250],
                "accrediti": [300, 340],
                "operazione": [390, 600]
            }, 
            interesting_area=[0,100,-1,800],
            required_columns=['data', 'operazione'],
            possible_multiple_rows=['operazione'],
            stop_fn=lambda value, values: value['operazione'] == 'SALDO FINALE'
        )
    elif provider_name == 'postepay-evolution-lista-movimenti': 
        data = parse_pdf(
            path=file, 
            columns={
                "data": [80, 100],
                "valuta": [130, 160],
                "operazione": [180, 490],
                "addebiti": [480, 510],
                "accrediti": [540, 600],
            }, 
            first_page_interesting_area=[0,230,-1,800],
            interesting_area=[0,100,-1,800],
            required_columns=['data', 'operazione'],
            possible_multiple_rows=['operazione'],
            stop_fn=lambda value, values: value['operazione'] == 'SALDO FINALE'
        )
    else:
        raise Exception(f"Provider {provider_name} not supported")
    
   
    def to_float(value):
        return float(value.replace('_', '').replace('.', '').replace(',', '.')) if value else 0

    exclude_rows = ["GIACENZA MEDIA NEL PERIODO"]

    # test 
    saldo_iniziale, saldo_finale, totale_entrate, totale_uscite, addebiti, accrediti = 0, 0, 0, 0, 0, 0

    filtered_data = []
    # for row in data with index
    for index, row in enumerate(data):
        if row['operazione'] in exclude_rows:
            continue

        row['import_hash'] = hashlib.sha256(f'{str(index)}_{str(row)}'.encode()).hexdigest()
        if row['operazione'] == 'TOTALE ENTRATE':
            totale_entrate = to_float(row['accrediti'])
        elif row['operazione'] == 'TOTALE USCITE':
            totale_uscite = to_float(row['addebiti'])
        elif row['operazione'] == 'SALDO INIZIALE':
            saldo_iniziale = to_float(row['accrediti'])
        elif row['operazione'] == 'SALDO FINALE':
            saldo_finale = to_float(row['accrediti'])
            #print(f"saldo finale {saldo_finale}", row)
        else:
            addebiti += to_float(row['addebiti'])
            accrediti += to_float(row['accrediti']) 
            filtered_data.append(row)

    accrediti = round(accrediti, 4)
    addebiti = round(addebiti, 4)
    differenza = round(accrediti - addebiti, 4)
    saldo_finale_calcolato = round(differenza + saldo_iniziale, 4)

    if provider_name != 'postepay-evolution-lista-movimenti':
        if totale_entrate:
            if totale_entrate != accrediti:
                raise Exception(f"Totale entrate {totale_entrate} different from calculated {accrediti}")
        if totale_uscite:
            if totale_uscite != addebiti:
                raise Exception(f"Totale uscite {totale_uscite} different from calculated {addebiti}")
        if saldo_finale != saldo_finale_calcolato:
            raise Exception(f"Saldo finale {saldo_finale} different from calculated {saldo_finale_calcolato}")

        print(f"[OK] file {file} per il provider {provider_name} importato corretamente")
    else:
        print(f"[OK - not controlled] file {file} per il provider {provider_name} importato corretamente")

    return filtered_data