# sources/object-store/garage/src/db/test.rs

Purpose: shared conformance tests for every enabled `garage_db` backend.

Important APIs/types/functions: `test_suite`, feature-gated tests `test_lmdb_db`, `test_sqlite_db`, and `test_fjall_db`.

Control flow: creates a tree, tests insert/get, transaction commit, transaction abort rollback, outside-transaction iteration/ranges/reverse iteration, and equivalent inside-transaction iterators. Each feature-specific test constructs a temporary or in-memory database and runs the same suite.

State and persistence: LMDB and Fjall tests use temporary directories; SQLite uses an in-memory connection manager. Test data is small fixed byte slices.

Dependencies and integration points: uses all public DB APIs and feature-gated adapter constructors. The suite is a contract for engine parity.

Risks: coverage is intentionally basic; it does not cover `clear`, `snapshot`, `import`, `on_commit`, concurrent access, large values, invalid tree IDs, or adapter-specific durability flags.

Test signals: direct unit tests are strong smoke tests for ordering and transaction semantics across enabled engines.
