from datetime import datetime,timezone,timedelta
from decimal import Decimal
import duckdb
import pytest
from migration_audit.source import SQLSource,identifier
from migration_audit.compare import audit,canonical

def test_streaming_merge_and_bounded_samples():
    left,right=duckdb.connect(),duckdb.connect()
    try:
        for db in [left,right]:
            db.execute('CREATE TABLE orders AS SELECT i AS id,i*10 AS amount FROM range(1000) t(i)')
        right.execute('DELETE FROM orders WHERE id<10')
        right.execute('UPDATE orders SET amount=9 WHERE id=15')
        right.execute('INSERT INTO orders VALUES(2000,1)')
        result=audit(SQLSource(left,'orders','id',7),SQLSource(right,'orders','id',11),max_samples=3)
        assert result['counts']=={'equal':989,'changed':1,'missing':10,'extra':1}
        assert len(result['samples'])==3 and not result['matched']
        assert result['source_digest']!=result['target_digest']
    finally:
        left.close();right.close()

def test_duplicate_key_and_sql_identifier_rejected():
    with pytest.raises(ValueError):
        identifier('orders; DROP TABLE orders')
    db=duckdb.connect()
    db.execute('CREATE TABLE t AS SELECT 1 id UNION ALL SELECT 1')
    with pytest.raises(ValueError):
        SQLSource(db,'t','id').validate()
    db.close()

def test_cross_type_numeric_and_timezone_normalization():
    assert canonical({'x':Decimal('1.00')})==canonical({'x':1})
    assert canonical({'x':Decimal('123456789012345678901234567890.12')})!=canonical({'x':Decimal('123456789012345678901234567890.13')})
    assert canonical({'x':datetime(2025,1,1,tzinfo=timezone.utc)})==canonical({'x':datetime(2024,12,31,16,tzinfo=timezone(timedelta(hours=-8)))})
    with pytest.raises(ValueError):
        canonical({'x':float('nan')})
