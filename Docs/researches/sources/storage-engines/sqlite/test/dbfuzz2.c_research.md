# sources/storage-engines/sqlite/test/dbfuzz2.c

## Purpose
`dbfuzz2.c` is a libFuzzer-oriented database-image fuzzer. Each fuzz input is treated as a serialized SQLite database, deserialized into an in-memory database, and exercised with a fixed suite of SQL statements covering integrity checks, schema scanning, dbstat, DML, ALTER TABLE, REINDEX, DROP, and VACUUM.

## Important APIs, Types, and Functions
- Fuzzer entry points: `LLVMFuzzerInitialize()` parses libFuzzer-compatible options; `LLVMFuzzerTestOneInput()` runs one input.
- SQL corpus: `azSql[]` contains fixed statements run against each input.
- Limits and observability: globals `eVerbosity`, `bVdbeDebug`, `szMax`, `nCb`, and `mxCb`; `progress_handler()` interrupts long-running statements.
- Memory tracing: `sqlite3MemTraceActivate()`, `sqlite3MemTraceDeactivate()`, and the `memtrace*` allocator methods wrap SQLite's allocator via `SQLITE_CONFIG_MALLOC`.
- Standalone mode: `readFile()` and `main()` are compiled under `STANDALONE`.

## Control Flow
Initialization filters custom options (`-v`, `--vdbe-debug`, `--limit`, `--memtrace`, `--max-db-size`, `--lookaside`, and Unix resource limits) out of argv before libFuzzer sees the rest. Each fuzz input initializes SQLite, opens an anonymous in-memory connection, copies the input into SQLite-owned memory, calls `sqlite3_deserialize()` with resize/free-on-close flags, applies a size limit file-control, optionally enables VDBE debug and progress callbacks, seeds SQLite PRNG deterministically, then executes every SQL statement in `azSql[]`. After close, it treats any remaining SQLite memory as a fatal leak.

## State and Persistence Behavior
All database content is transient and backed by the deserialized input buffer. `SQLITE_DESERIALIZE_FREEONCLOSE` transfers ownership to the database connection. `SQLITE_FCNTL_SIZE_LIMIT` bounds growth during statements such as `VACUUM`. The memory-tracing allocator is global SQLite configuration state, installed before initialization.

## Dependencies and Integration Points
The file integrates with libFuzzer's `LLVMFuzzer*` hooks, SQLite deserialize/file-control/progress APIs, `dbstat` when compiled with `SQLITE_ENABLE_DBSTAT_VTAB`, optional `SQLITE_TESTCTRL_PRNG_SEED`, and platform `setrlimit()` controls on non-Windows systems.

## Risks and Edge Cases
Because it checks `sqlite3_memory_used()` after every input, allocator configuration and all SQLite cleanup paths must be deterministic. Inputs can trigger writes through ALTER/DML/VACUUM, so size limits and progress callbacks are important guardrails. `sqlite3_open(0, &db)` and deserialize behavior depend on SQLite memory-db support. Option parsing mutates `argv` in place, so fuzzer arguments must be preserved carefully.

## Test Signals
libFuzzer reports crashes, sanitizer findings, hangs, and exits. This file additionally emits memory-leak failures, close errors, optional verbose SQL result codes, progress-limit messages, and resource-limit diagnostics.
