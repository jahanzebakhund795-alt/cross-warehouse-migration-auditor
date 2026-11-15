import argparse
import json
from pathlib import Path
import duckdb
from .source import SQLSource,postgres_source
from .compare import audit

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-parquet',required=True)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--target-duckdb')
    group.add_argument('--target-postgres-dsn')
    parser.add_argument('--table',required=True)
    parser.add_argument('--key',required=True)
    parser.add_argument('--output',default='output/audit.json')
    args=parser.parse_args()
    left=duckdb.connect()
    left.read_parquet(args.source_parquet).create_view('source_data')
    source=SQLSource(left,'source_data',args.key)
    if args.target_duckdb:
        right=duckdb.connect(args.target_duckdb,read_only=True)
        target=SQLSource(right,args.table,args.key)
    else:
        target=postgres_source(args.target_postgres_dsn,args.table,args.key)
        right=target.connection
    try:
        result=audit(source,target)
        output=Path(args.output)
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))
        return 0 if result['matched'] else 1
    finally:
        left.close()
        right.close()
if __name__=='__main__':
    raise SystemExit(main())
