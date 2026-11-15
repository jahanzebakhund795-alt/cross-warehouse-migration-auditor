# Cross Warehouse Migration Auditor

A newly built portfolio implementation for Jahanzeb Akhund, aligned with the data architecture and engineering work described in his resume. All example data is synthetic. This repository is independent sample work; it does not contain employer code, claim a historical deployment, or reproduce resume performance metrics.

## Implemented system

A bounded-memory migration auditor merge-compares ordered database cursors, validates primary-key uniqueness, canonicalizes cross-engine numeric and timestamp values, computes full-stream SHA-256 digests, and emits bounded discrepancy samples with complete difference counts. It includes real Parquet/DuckDB and PostgreSQL DB-API adapters, a CLI with meaningful exit codes, and a 5,000-row fault-injection fixture.

[Architecture diagram and design review](docs/ARCHITECTURE.md)

## Run

Use Python 3.11 for the documented development environment.

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[test]"
pytest -q
python scripts/seed.py
# This fixture intentionally differs; exit code 1 is expected:
python -m migration_audit.cli --source-parquet output/source.parquet --target-duckdb output/target.duckdb --table orders --key id
```

## Design and operating limits

Source and target must represent the same extraction cut. PostgreSQL uses a read-only repeatable-read transaction; cross-system snapshot coordination remains an orchestration responsibility. The key must be one consistently typed, consistently collated sortable column. Column names and values are audited; physical storage types are not declared equivalent. Monetary comparison is exact, not tolerance-based. PostgreSQL integration requires a live server; local tests exercise DuckDB cursor streaming.

See [the operating guide](docs/OPERATIONS.md) for recovery, deployment, and validation boundaries. An optional GitHub Actions definition is in `docs/ci-template.yml`; enabling it requires installing it under `.github/workflows/` with workflow permission.

## References

- [DuckDB Python API](https://duckdb.org/docs/stable/clients/python/overview)
- [Psycopg transactions](https://www.psycopg.org/psycopg3/docs/basic/transactions.html)

## Executed validation

3 pytest tests passed. Cursor merge comparison, bounded samples, duplicate keys, exact large decimal and timezone normalization, plus an actual 5,000-row Parquet/DuckDB run detecting five missing, three changed, and one extra record.

[Full validation evidence and limits](VALIDATION.md)
