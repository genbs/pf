import psycopg2
import datetime
import os 

conn = None
cursor = None

def init():
    global conn, cursor
    
    database='pf'
    user='postgres'
    password=''
    host='localhost'
    port='5432'

    location = f'../backups/{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.sql'
    command = f'pg_dump -U {user} -h {host} -p {port} -d {database} -W -f {location}'
    os.system(command)
    
    conn = psycopg2.connect(
        database=database,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cursor = conn.cursor()  

    # get ../db.sql file
    with open('../db.sql', 'r') as file:
        sql = file.read()
        cursor.execute(sql)
    
    conn.commit()

def query(sql, values = None):
    if values:
        cursor.execute(sql, values)
    else:
        cursor.execute(sql)
    conn.commit()
    return cursor.fetchall()


def insert(table, data):
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['%s'] * len(data))
    values = tuple(data.values())
    query = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
    cursor.execute(query, values)
    conn.commit()
    cursor.execute('SELECT LASTVAL()')
    last_id = cursor.fetchone()[0]
    if not last_id:
        raise Exception('Error inserting data', data)
    return last_id

def find(table, columns, property, value):
    cursor.execute(f'SELECT {columns} FROM {table} WHERE LOWER({property}) LIKE ?', (f'%{value.lower()}%',))
    return cursor.fetchall()

def select(table, columns = '*', where = None):
    if where:
        values = tuple(where.values())
        placeholders = ' AND '.join(f'{key} = %s' for key in where.keys())
        cursor.execute(f'SELECT {columns} FROM {table} WHERE {placeholders}', values)
    else:
        cursor.execute(f'SELECT {columns} FROM {table}')
    return cursor.fetchall()

def select_one(table, columns = '*', where = None):
    if where:
        values = tuple(where.values())
        placeholders = ' AND '.join(f'{key} = %s' for key in where.keys())
        cursor.execute(f'SELECT {columns} FROM {table} WHERE {placeholders}', values)
    else:
        cursor.execute(f'SELECT {columns} FROM {table}')
    return cursor.fetchone()

def update(table, data, where):
    placeholders = ', '.join(f'{key} = %s' for key in data.keys())
    values = tuple(data.values())
    cursor.execute(f'UPDATE {table} SET {placeholders} WHERE {where}', values)
    conn.commit()

def close():
    cursor.close()
    conn.close()