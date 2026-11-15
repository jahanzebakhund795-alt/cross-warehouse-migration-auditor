import re

def identifier(value):
    parts=value.split('.')
    if not all(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',p) for p in parts):
        raise ValueError('Unsafe SQL identifier')
    return '.'.join('"'+p+'"' for p in parts)

class SQLSource:
    def __init__(self,connection,table,key,batch_size=500):
        self.connection=connection
        self.table=identifier(table)
        self.key=key
        self.quoted_key=identifier(key)
        self.batch_size=batch_size

    def validate(self):
        cursor=self.connection.cursor()
        try:
            cursor.execute(f'SELECT * FROM {self.table} LIMIT 0')
            columns=[item[0] for item in cursor.description]
            if self.key not in columns or len(set(columns))!=len(columns):
                raise ValueError('Missing primary key or duplicate column names')
            cursor.execute(f'SELECT {self.quoted_key},COUNT(*) FROM {self.table} GROUP BY {self.quoted_key} HAVING {self.quoted_key} IS NULL OR COUNT(*)>1 LIMIT 1')
            if cursor.fetchone():
                raise ValueError('Null or duplicate primary key')
            return columns
        finally:
            cursor.close()

    def rows(self):
        from uuid import uuid4
        cursor=(self.connection.cursor(name='audit_'+uuid4().hex)
                if type(self.connection).__module__.startswith('psycopg') else self.connection.cursor())
        try:
            cursor.execute(f'SELECT * FROM {self.table} ORDER BY {self.quoted_key}')
            columns=[item[0] for item in cursor.description]
            while True:
                batch=cursor.fetchmany(self.batch_size)
                if not batch:
                    return
                for row in batch:
                    yield dict(zip(columns,row))
        finally:
            cursor.close()

def postgres_source(dsn,table,key):
    import psycopg
    connection=psycopg.connect(dsn)
    connection.execute('BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
    # The caller owns connection lifetime and must close it after audit.
    return SQLSource(connection,table,key)
