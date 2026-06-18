## sources/object-store/rustfs/crates/targets/tests/postgres_integration.rs

Purpose: integration tests for the PostgreSQL notification target. Most tests are ignored because they require a running PostgreSQL server; one identifier validation test runs without a database.

Important APIs/types/functions: `test_args` builds `PostgresArgs` from `RUSTFS_TEST_PG_DSN` or a localhost default and copies schema parsed by `PostgresDsn`. `with_search_path` rewrites DSN query parameters. `raw_client` opens a `tokio_postgres` client with `NoTls` and spawns the connection future. `unique_table` and `entity_for` provide isolation helpers.

Control flow and state: probe tests verify an existing table succeeds and a missing table fails. Namespace format creates a key/value table and asserts two saves for the same key collapse via upsert. Access format creates an append table and asserts distinct events create two rows. Replay idempotency is simulated with direct SQL using `ON CONFLICT (event_id) DO NOTHING`. Init succeeds against an existing namespace table. The non-ignored malicious table name test verifies construction rejects unsafe identifiers.

Dependencies and integration points: exercises `PostgresTarget`, `PostgresDsn`, `PostgresFormat`, `check_postgres_server_available`, `tokio_postgres`, URL manipulation, and serde JSON event payloads.

Risks: database tests are ignored by default and depend on manual environment. `raw_client` uses `NoTls`, while target TLS behavior is not covered here. Dynamic SQL uses quoted generated identifiers; identifier validation is critical and directly tested for malicious input.

Test signals: documents namespace upsert semantics, access append semantics, access replay idempotency via event id conflict, connectivity errors, init behavior, and identifier validation.
