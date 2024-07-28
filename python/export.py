import xlsxwriter

from db.db import init as init_db, select
from db.utils import find_or_create_account, add_transaction_if_not_exists

init_db()

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


def generateXLS(path):
    workbook = xlsxwriter.Workbook(path)
    workbook.set_calc_mode('auto')
    return workbook

# esporta gli account
workbook = generateXLS('../exports/accounts.xlsx')
bold = workbook.add_format({'bold': True})

accounts = select('accounts', 'id, name, reference')
worksheet = workbook.add_worksheet('Accounts')

worksheet.write(0, 0, 'ID', bold)
worksheet.write(0, 1, 'Name', bold)
worksheet.write(0, 2, 'Reference', bold)

for i, account in enumerate(accounts):
    worksheet.write(i + 1, 0, account[0])
    worksheet.write(i + 1, 1, account[1])
    worksheet.write(i + 1, 2, account[2])

print(f"Data exported to ../exports/accounts.xlsx")
workbook.close()


# seleziona il minimo e il massimo anno
years = select('transactions', 'MIN(started_date), MAX(started_date)', {'account_id': 3})
min_year = years[0][0].year
max_year = years[0][1].year

print(f"Exporting data from {min_year} to {max_year}")

bold = workbook.add_format({'bold': True})
money = workbook.add_format({'num_format': '#,##0.00'})
datetime_format = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})

for year in range(min_year, max_year + 1):
    workbook = generateXLS(f'../exports/transactions/transactions_{year}.xlsx')

    for month in range(1, 13):
        transactions = select('transactions', 'started_date, completed_date, description, amount, fee, currency, type, account_id', {'EXTRACT(YEAR FROM started_date)': year, 'EXTRACT(MONTH FROM started_date)': month, 'account_id': 3})
        # if not transactions:
        #     continue
        
        month_human = MONTHS[month - 1]
        worksheet = workbook.add_worksheet(f'{month_human}_{year}')

        worksheet.write(0, 0, 'Started', bold)
        worksheet.write(0, 1, 'Completed', bold)
        worksheet.write(0, 2, 'Description', bold)
        worksheet.write(0, 3, 'Amount', bold)
        worksheet.write(0, 4, 'Fee', bold)
        worksheet.write(0, 5, 'Currency', bold)
        worksheet.write(0, 6, 'Type', bold)
        worksheet.write(0, 7, 'Account', bold)

        row = 1
        for record in transactions:
            worksheet.write(row, 0, record[0].strftime('%Y-%m-%d %H:%M:%S'), datetime_format)
            worksheet.write(row, 1, record[1].strftime('%Y-%m-%d %H:%M:%S'), datetime_format)
            worksheet.write(row, 2, record[2])
            worksheet.write(row, 3, record[3], money)
            worksheet.write(row, 4, record[4], money)
            worksheet.write(row, 5, record[5])
            worksheet.write(row, 6, record[6])
            worksheet.write(row, 7, record[7])
            row = row + 1


    # genero una pagina con il recap entrate/uscite per mese

    summary_sheet = workbook.add_worksheet('Summary')

    # creo una riga con i mesi, la prima colonna è il tipo (incoming/outgoing)
    summary_sheet.write(0, 0, 'Type', bold)
    for i, month in enumerate(MONTHS):
        summary_sheet.write(0, i + 1, month, bold)
    
    # per ogni mese prendo le colonne e sommo filtrando per il tipo
    for i, trans_type in enumerate(['incoming', 'outgoing', 'total']):
        summary_sheet.write(i + 1, 0, trans_type, bold)
        for j, month in enumerate(MONTHS):
            worksheet_name = f'{month}_{year}'
            worksheet_month = workbook.get_worksheet_by_name(worksheet_name)
            if worksheet_month:
                start_row = 1
                end_row = worksheet_month.dim_rowmax + 1
                col_amount = xlsxwriter.utility.xl_col_to_name(3)  # Colonna D
                col_fee = xlsxwriter.utility.xl_col_to_name(4)    # Colonna E
                col_type = xlsxwriter.utility.xl_col_to_name(6)   # Colonna G

                if trans_type == 'incoming':
                    formula = f"SUMIFS('{worksheet_name}'!${col_amount}${start_row}:${col_amount}${end_row}, '{worksheet_name}'!${col_type}${start_row}:${col_type}${end_row}, \"{trans_type}\") - SUMIFS('{worksheet_name}'!${col_fee}${start_row}:${col_fee}${end_row}, '{worksheet_name}'!${col_type}${start_row}:${col_type}${end_row}, \"{trans_type}\") "
                elif trans_type == 'outgoing':
                    formula = f"SUMIFS('{worksheet_name}'!${col_amount}${start_row}:${col_amount}${end_row}, '{worksheet_name}'!${col_type}${start_row}:${col_type}${end_row}, \"{trans_type}\") + SUMIFS('{worksheet_name}'!${col_fee}${start_row}:${col_fee}${end_row}, '{worksheet_name}'!${col_type}${start_row}:${col_type}${end_row}, \"{trans_type}\") "
                else:
                    incoming_col = f"{xlsxwriter.utility.xl_col_to_name(j + 1)}2"
                    outgoing_col = f"{xlsxwriter.utility.xl_col_to_name(j + 1)}3"
                    formula = f"{incoming_col} - {outgoing_col}"
                    # voglio colorare di rosso se il valore è negativo, altrimenti verder
                    summary_sheet.conditional_format(i + 1, j + 1, i + 1, j + 1, {'type': 'cell', 'criteria': '<', 'value': 0, 'format': workbook.add_format({'bg_color': '#FFC7CE'})})
                    summary_sheet.conditional_format(i + 1, j + 1, i + 1, j + 1, {'type': 'cell', 'criteria': '>', 'value': 0, 'format': workbook.add_format({'bg_color': '#C6EFCE'})})

                summary_sheet.write_formula(i + 1, j + 1, formula, None, '')
        summary_sheet.write(i + 1, 13, f'=SUM(B{i + 2}:M{i + 2})', None, '')

    workbook.close()
    print(f"Data exported to ../exports/transactions/transactions_{year}.xlsx")