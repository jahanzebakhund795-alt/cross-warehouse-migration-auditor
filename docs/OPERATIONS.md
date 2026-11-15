# Operating guide

## Deployment contract

Source and target must represent the same extraction cut. PostgreSQL uses a read-only repeatable-read transaction; cross-system snapshot coordination remains an orchestration responsibility. The key must be one consistently typed, consistently collated sortable column. Column names and values are audited; physical storage types are not declared equivalent. Monetary comparison is exact, not tolerance-based. PostgreSQL integration requires a live server; local tests exercise DuckDB cursor streaming.

Keep credentials in environment variables or a secret manager; `.env` is ignored. Example credentials, when present, are for isolated local development. No service in this portfolio is represented as an audited HIPAA/GDPR system.

## Change and recovery procedure

Run the tests before deploying. Start with synthetic fixtures, retain the input batch or event offset, and inspect rejected records before replaying. The source code and tests specify the idempotency keys and transactional boundaries. Do not bypass those boundaries to repair a failed load.

For a real service, define retention and backup policies, TLS, identity federation, per-role permissions, dependency patching, resource limits, and alert destinations. Containers and local files demonstrate deployment contracts; operating these integrations at scale requires load and failure testing in the target environment.

## Validation evidence

`VALIDATION.md` records checks actually executed when this portfolio was prepared. Integration commands requiring external services are explicitly distinguished from executed local tests. No availability, throughput, cost-saving, or compliance guarantee is inferred from unit tests.
