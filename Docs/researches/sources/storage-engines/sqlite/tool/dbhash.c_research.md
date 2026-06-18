# sources/storage-engines/sqlite/tool/dbhash.c

## Purpose
`dbhash.c` computes a SHA1 hash of logical SQLite database content rather than raw file bytes. The hash ignores free space and representation details such as page size, encoding, and auto-vacuum, making it useful for verifying semantic database equivalence across rebuilds or transformations.

## Important APIs, Types, and Functions
`SHA1Context` stores SHA1 state, bit counts, and a block buffer. `GlobalVars` holds program name, debug flags, the open SQLite handle, and hash context. `SHA1Transform()`, `hash_init()`, `hash_step()`, and `hash_finish()` implement SHA1. `db_prepare()` and `db_vprepare()` wrap `sqlite3_vmprintf()` and `sqlite3_prepare_v2()`. `hash_one_query()` steps a query and feeds typed column encodings into the hash. `main()` parses options and drives hashing for each database.

## Control Flow
The program parses `--debug`, `--like`, `--schema-only`, `--without-schema`, and filenames. For each database it opens read/write URI mode so hot journals can recover, validates the schema, initializes SHA1, optionally hashes table content for non-virtual, non-`sqlite_%` tables matching the LIKE pattern, optionally hashes schema rows, emits the digest and filename, and closes the connection.

## State and Persistence
Logical hash state is in `g.cx`. The database is opened read/write, so SQLite may perform recovery as a side effect. No application tables are modified. The process prints one digest per input file.

## Dependencies and Integration Points
It depends on SQLite and the C runtime. It is a SQLite test tool for comparing databases independent of physical layout. It uses `sqlite_schema`, type-specific `sqlite3_column_*()` accessors, and SQLite identifier quoting through `%w`.

## Risks
The content query omits explicit `ORDER BY`, relying on historical primary-key order for full table scans, which is called out in the comments but is not a SQL guarantee. It excludes virtual tables and `sqlite_%` system tables from content hashing. Floating point hashing uses in-memory binary representation, which is stable within supported platforms but still low-level. The diagnostic check for mutually exclusive options mentions `--omit-schema` although the actual option is `--schema-only`.

## Test Signals
Equivalent databases with different page sizes should hash identically. Data changes, schema changes, and `--like` filters should change or limit the digest. `--schema-only` and `--without-schema` should isolate schema/content differences. Debug mode should trace typed values to stderr.
