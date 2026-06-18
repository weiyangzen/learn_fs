# sources/storage-engines/sqlite/ext/fts3/fts3_aux.c

## Purpose
`fts3_aux.c` implements the `fts4aux` virtual table module. `fts4aux` exposes term-level statistics for an existing FTS3/FTS4 table as a read-only table with columns `term`, `col`, `documents`, `occurrences`, and hidden `languageid`. It is an inspection/debug/statistics interface over the FTS segment index rather than a table with its own persistent storage.

## Important APIs, Types, And Functions
`Fts3auxTable` embeds `sqlite3_vtab` and owns a minimal `Fts3Table` instance used to address the target FTS table's segment tables. It does not create independent shadow tables.

`Fts3auxCursor` embeds `sqlite3_vtab_cursor` followed immediately by `Fts3MultiSegReader`, plus a `Fts3SegFilter`, optional stop term, language id, EOF flag, synthetic rowid, current column index, and an expandable `aStat` array. Each `aStat` entry stores per-term document and occurrence counts for all columns (`col='*'`) and individual columns.

The module schema is `CREATE TABLE x(term, col, documents, occurrences, languageid HIDDEN)`. `sqlite3Fts3InitAux(sqlite3 *db)` registers the module name `fts4aux` with SQLite.

The vtab callbacks are `fts3auxConnectMethod()` for both xCreate and xConnect, `fts3auxDisconnectMethod()` for xDisconnect/xDestroy, `fts3auxBestIndexMethod()`, `fts3auxOpenMethod()`, `fts3auxCloseMethod()`, `fts3auxFilterMethod()`, `fts3auxNextMethod()`, `fts3auxEofMethod()`, `fts3auxColumnMethod()`, and `fts3auxRowidMethod()`.

## Control Flow
`fts3auxConnectMethod()` accepts either `CREATE VIRTUAL TABLE aux USING fts4aux(fts_table)` or the temp-table form with an explicit target database and FTS table. It declares the fixed schema, allocates one block containing `Fts3auxTable`, a minimal `Fts3Table`, and copied database/table names, dequotes the target table name, sets `db`, `zDb`, `zName`, and `nIndex=1`, and returns the vtab object.

`fts3auxBestIndexMethod()` advertises that output is naturally ordered by `term ASC`, recognizes equality and range constraints on `term`, recognizes equality on hidden `languageid`, assigns argument indexes, and reduces estimated cost for constrained scans. Equality on `term` is cheapest; range scans are intermediate; unconstrained scans are expensive.

`fts3auxFilterMethod()` resets any reused cursor, interprets `idxNum` to pull `term=?`, `term>=?`, `term<=?`, and optional `languageid=?` values, builds a segment filter with required positions and empty-doclist filtering, enables scan mode for ranges, stores a lower-bound term and optional upper stop term, clamps negative language ids to zero, opens a segment-reader cursor over all segments for the target language, starts it, and advances once through `fts3auxNextMethod()`.

`fts3auxNextMethod()` first emits any remaining per-column rows for the current term whose document count is non-zero. Once columns are exhausted, it steps the multi-segment reader to the next term. For each doclist, it decodes the FTS3 doclist state machine: docid, optional column markers, and positions. It accumulates `aStat[0]` for all columns and `aStat[iCol+1]` for individual columns, then starts returning rows from `col='*'` onward. If a configured stop term is passed, it marks EOF.

`fts3auxColumnMethod()` returns the current term, column (`'*'` for aggregate or zero-based integer column index), document count, occurrence count, or current language id. `fts3auxCloseMethod()` closes segment resources and frees cursor buffers.

## State And Persistence Behavior
`fts4aux` has no persistent representation of its own. xCreate and xConnect are identical, and xDestroy and xDisconnect just release in-memory resources. The module reads the target FTS table's `%_segments`/`%_segdir` data through the common FTS3 segment-reader API.

Cursor state is transient. `aStat` grows as needed for terms whose doclists reference higher column numbers, and is zeroed for each new term. `iRowid` is a synthetic monotonically increasing rowid unrelated to the target FTS table rowids. `zStop` bounds range scans in memory after the segment reader begins at the lower bound.

The minimal embedded `Fts3Table` only contains the fields needed by segment-reader helpers and statement caches. `fts3auxDisconnectMethod()` finalizes any cached statements in that embedded object and frees `zSegmentsTbl`.

## Dependencies
The file depends on `fts3Int.h`, SQLite virtual-table APIs, string/assert helpers, and shared FTS3 functions: `sqlite3Fts3Dequote()`, `sqlite3Fts3ErrMsg()`, `sqlite3Fts3SegmentsClose()`, `sqlite3Fts3SegReaderFinish()`, `sqlite3Fts3SegReaderCursor()`, `sqlite3Fts3SegReaderStart()`, `sqlite3Fts3SegReaderStep()`, and `sqlite3Fts3GetVarint()`.

It relies on FTS3 doclist encoding constants and `Fts3Table.nColumn` as discovered by segment-reader preparation. It is compiled only when FTS3 is available outside omitted/core-disabled configurations.

## Integration Points
`sqlite3Fts3Init()` calls `sqlite3Fts3InitAux()` during FTS3 initialization, so connections with FTS3 get the `fts4aux` module too. Users create an auxiliary virtual table pointing at an existing FTS table and query it with ordinary SQL. The module's hidden `languageid` column integrates with FTS4 language-id indexing.

The implementation shares the exact segment-reader path used by FTS queries. That makes `fts4aux` useful as a test and diagnostic view of the term index: it scans real index doclists and decodes position lists without going through expression parsing or content-table lookup.

## Risks And Edge Cases
The doclist decoder must reject malformed column markers. If a decoded column number is less than 1 or greater than `nColumn+1`, `fts3auxNextMethod()` returns `SQLITE_CORRUPT_VTAB`. The state machine also assumes valid FTS3 position-list encoding, so corruption tests should exercise truncated varints, bad column transitions, and malformed terminators.

Constructor argument handling is intentionally narrow. The two-table-name form is accepted only for temp-created aux tables that name a target database explicitly; other argument counts or database forms return an error message. A missing or stale target FTS table will surface later through segment-reader preparation rather than through a persistent aux schema check.

Range boundaries are byte-string comparisons over terms. The stop check marks EOF once the current term is greater than the upper bound or has the upper bound as a strict prefix-extension beyond it. Negative language ids are clamped to zero because SQLite's outer constraint check will reject returned rows for the original negative value.

## Test Signals
Tests should create FTS3/FTS4 tables, populate multiple columns and language ids, then verify `fts4aux` aggregate and per-column `documents`/`occurrences` counts. Query planner tests should cover unconstrained scans, `ORDER BY term ASC`, `term=?`, lower/upper range constraints, combined range constraints, and `languageid=?`.

Robustness tests should exercise empty indexes, deleted/updated rows, prefix-index tables, terms appearing in only some columns, malformed segment data, cursor reuse across filters, and cleanup paths that finalize cached statements and close segment readers.
