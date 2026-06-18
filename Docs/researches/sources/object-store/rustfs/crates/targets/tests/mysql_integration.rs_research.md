## sources/object-store/rustfs/crates/targets/tests/mysql_integration.rs

Purpose: ignored integration tests for the MySQL/TiDB notification target, covering direct writes, queue replay, duplicate replay semantics, schema validation, and connectivity probing.

Important APIs/types/functions: `test_dsn` requires `RUSTFS_TEST_MYSQL_DSN`. `table_name` creates short UUID-suffixed table names. `make_args` builds `MySqlArgs` with empty TLS paths, queue limit, format `access`, and max open connections. `make_entity` constructs event entities. `build_test_pool` parses `MySqlDsn`, configures `mysql_async::OptsBuilder`, and installs the rustls aws-lc provider when TLS is requested. `drop_table` cleans up.

Control flow and state: direct write initializes target/table, saves one event, and verifies one row with bucket data. Delete test verifies PUT and DELETE events append separate rows. Queue test saves to store before init, verifies zero DB rows before replay, replays store keys, and checks queue empty. Duplicate replay decodes `QueuedPayload`, sends raw payload twice with the same key metadata, and expects duplicate rows, documenting MySQL at-least-once behavior. Incompatible schema test expects `TargetError::Initialization`. Connectivity test succeeds against an existing compatible table.

Dependencies and integration points: exercises `mysql_async`, target queue store, `QueuedPayload`, MySQL DSN parsing, SQL schema initialization, and `check_mysql_server_available`.

Risks: ignored tests require external MySQL/TiDB and manual setup. Duplicate replay intentionally produces duplicates, so consumers need downstream idempotency if required. Table identifiers are generated but SQL formatting still relies on target-side validation.

Test signals: strong documentation for MySQL target delivery semantics; not run by default CI.
