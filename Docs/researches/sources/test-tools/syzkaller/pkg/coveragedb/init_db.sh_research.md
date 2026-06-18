# sources/test-tools/syzkaller/pkg/coveragedb/init_db.sh

Purpose: initializes the Cloud Spanner `coverage` database schema used by `coveragedb.go`.

Important operations: drops and recreates tables `files`, `functions`, `merge_history`, and `file_subsystems`; creates index `merge_history_session`.

Control flow: the script uses `set -e` and `pipefail`, then runs sequential `gcloud spanner databases ddl update` calls against instance `syzbot`, project `syzkaller`, database `coverage`. Table DDL strings are built with `echo -n` and passed as `--ddl`.

State and persistence: destructive persistent database changes. It drops existing tables before creating replacements, so it deletes stored coverage data.

Dependencies and integration: requires authenticated `gcloud`, Cloud Spanner access, and schema alignment with `coveragedb` struct field names and mutation builders.

Risks: highly destructive and hard-coded to production-looking project/instance names. It uses PostgreSQL-like type names (`text`, `bigint`, `timestamptz`) in Spanner DDL, implying a specific dialect. No confirmation prompt or environment guard exists.

Test signals: no tests. Operational safety depends on manual usage discipline.
