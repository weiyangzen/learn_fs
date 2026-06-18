# sources/storage-engines/sqlite/ext/fts3/tool/fts3view.c

## Purpose
`fts3view.c` is a standalone debugging and analysis utility for SQLite FTS3/FTS4 indexes. Linked against a SQLite build with `SQLITE_ENABLE_FTS4`, it opens a database, lists FTS3/4 tables, or inspects an FTS table's schema, statistics, vocabulary, segment layout, raw segment bytes, decoded segment nodes, decoded doclists, and largest segment blocks.

## Important APIs, Types, And Functions
Global command parsing state is `nExtra` and `azExtra`. `findOption()` consumes simple `--name` and `--name value` options from that array.

SQLite helpers are `prepare()` and `runSql()`. `prepare()` formats SQL with `sqlite3_vmprintf()`, prepares it, and exits on error. `runSql()` formats and executes SQL and returns the SQLite result code.

Inspection commands are implemented by `showSchema()`, `showStat()`, `showVocabulary()`, `showSegmentStats()`, `showSegdirMap()`, `showSegment()`, `showDoclist()`, and `listBigSegments()`.

Binary format helpers are `getVarint()`, `decodeSegment()`, `printBlob()`, `atoi64()`, `prepareToGetSegment()`, and `decodeDoclist()`. These decode the FTS3 segment-node and doclist formats enough to print human-readable diagnostics.

`main()` opens the database, lists FTS tables when only a database argument is supplied, or dispatches `big-segments`, `doclist`, `schema`, `segdir`, `segment`, `segment-stats`, `stat`, or `vocabulary`.

## Control Flow
With one argument, `main()` scans `sqlite_schema` for `*_segdir` tables and prints the corresponding virtual-table creation SQL. With table and command arguments, it dispatches to one command handler and returns.

`showVocabulary()` creates a temporary `fts4aux` table with a randomized name inside a transaction, computes document count, token totals, rare-token counts, and top tokens, then rolls back so the auxiliary table is discarded.

`showSegmentStats()` aggregates `%_segments` and `%_segdir` sizes, splits leaf versus interior/root segments, consults `PRAGMA page_size`, counts oversized leaf blocks, and prints per-relative-level summaries.

`showSegdirMap()` iterates `%_segdir` grouped by index and level, prints root rowids as `r<rowid>`, maps tree and leaf block ranges, and identifies NULL marker blocks used by appendable incremental-merge segments.

`showSegment()` selects either a `%_segdir.root` blob (`rN`) or a `%_segments.block` blob (`N`), then either hex-dumps it with `printBlob()` or parses it with `decodeSegment()`. `showDoclist()` selects a segment/root blob, slices by offset and size, and either dumps or decodes the doclist.

## State And Persistence Behavior
The program is mostly read-only. It opens the target database and runs SELECT/PRAGMA queries against schema and FTS shadow tables. The main exception is `showVocabulary()`, which creates an `fts4aux` virtual table inside `BEGIN` and ends with `ROLLBACK`, making it intentionally temporary.

All output is written to stdout/stderr. The utility exits with status 1 for usage errors, open failures, or prepare failures. It does not attempt to recover from malformed command arguments or corrupt FTS blobs beyond basic parsing.

## Dependencies
The file depends on the SQLite C API and standard C headers. Runtime use requires an SQLite library built with FTS4 support so `fts4aux` and FTS3/FTS4 shadow-table conventions exist. It assumes legacy shadow-table names `%_segments`, `%_segdir`, and `%_stat`.

## Integration Points
This is a tooling companion for the FTS3/FTS4 storage format implemented by files such as `fts3_write.c`. It understands the same segment-node prefix compression, doclist varints, `%_segdir` block ranges, `root` blobs, and appendable NULL marker conventions. It is useful for diagnosing merge behavior, segment bloat, vocabulary distribution, and corrupt or suspicious segment records.

## Risks And Edge Cases
This is diagnostic code and uses process exits for many errors. It builds SQL with `%q`/`%Q` escaping for table names in most places, but it assumes trusted local use. `decodeSegment()` has a fixed 1000-byte term buffer and exits if a term is too long. `getVarint()` is permissive and does not receive a buffer length, so corrupt blobs can cause misleading output or unsafe reads if used outside controlled debugging. `showVocabulary()` uses `sqlite3_mprintf("viewer_%llx", zTab, r)` with an extra unused argument, harmless in practice but a sign that this is not production-path code.

## Test Signals
Useful checks include running the tool against a database with no FTS tables, a simple FTS3 table, an FTS4 table with `%_stat`, a table with prefix indexes, a database after optimize/incremental merge, and known segment/doclist offsets. The `--raw` and decoded modes should agree on blob sizes and offsets. Building the tool against the SQLite amalgamation with `SQLITE_ENABLE_FTS4` is the first validation gate.
