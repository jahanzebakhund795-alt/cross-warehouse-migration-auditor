from pathlib import Path
import duckdb

Path('output').mkdir(exist_ok=True)
with duckdb.connect('output/target.duckdb') as db:
    db.execute('CREATE OR REPLACE TABLE orders AS SELECT i AS id, (i*17)::BIGINT AS amount_cents FROM range(5000) t(i)')
    db.execute("COPY orders TO 'output/source.parquet' (FORMAT PARQUET)")
    db.execute('DELETE FROM orders WHERE id<5')
    db.execute('UPDATE orders SET amount_cents=amount_cents+1 WHERE id BETWEEN 10 AND 12')
    db.execute('INSERT INTO orders VALUES(6000,999)')
print('Seeded intentional differences: 5 missing, 3 changed, 1 extra.')
