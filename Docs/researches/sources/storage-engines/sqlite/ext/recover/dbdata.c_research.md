# sources/storage-engines/sqlite/ext/recover/dbdata.c

## Purpose

`dbdata.c` implements two eponymous virtual tables used by SQLite recovery tooling: `sqlite_dbdata` and `sqlite_dbptr`. Both read raw database pages through the `sqlite_dbpage` virtual table and bypass normal b-tree decoding. `sqlite_dbdata` extracts record fields from b-tree cells, tolerating corruption and returning as much data as possible. `sqlite_dbptr` emits parent-to-child page pointers from interior b-tree pages.

## Important APIs, Types, and Functions

`DbdataTable` is the virtual table object; it stores the SQLite connection, a reusable page-fetch statement, and `bPtr` to distinguish `sqlite_dbptr` from `sqlite_dbdata`. `DbdataCursor` stores scan position (`iPgno`, `iCell`, `iField`, `iRowid`), page buffer, page/cell counts, one-page mode, database size, encoding, record payload buffer, header/data pointers, and intkey rowid. `DbdataBuffer` is a reallocating byte buffer for record payloads.

Virtual table methods are registered in `sqlite3DbdataRegister()`. Core callbacks are `dbdataConnect()`, `dbdataDisconnect()`, `dbdataBestIndex()`, `dbdataOpen()`, `dbdataClose()`, `dbdataFilter()`, `dbdataNext()`, `dbdataEof()`, `dbdataColumn()`, and `dbdataRowid()`. The load/decode helpers are `dbdataLoadPage()`, `dbdataGetVarint()`, `dbdataGetVarintU32()`, `dbdataValueBytes()`, `dbdataValue()`, `dbdataDbsize()`, and `dbdataGetEncoding()`.

Schemas are declared as `sqlite_dbdata(pgno, cell, field, value, schema HIDDEN)` and `sqlite_dbptr(pgno, child, schema HIDDEN)`. `sqlite3_dbdata_init()` is the extension initializer and registers both modules unless virtual tables are omitted.

## Control Flow

`dbdataBestIndex()` recognizes equality constraints on hidden `schema` and visible `pgno`. With `schema=?`, the scan reads an attached database name or a special function-like schema source. With `pgno=?`, it switches to one-page mode and lowers estimated cost/rows. For `sqlite_dbdata`, it can also consume simple ascending ORDER BY clauses on `pgno` and `cell` when a page constraint exists.

`dbdataFilter()` resets the cursor, chooses the schema (default `main`), determines database size unless scanning one page, prepares or reuses a statement to fetch page bytes, binds the schema, reads page 1 to determine text encoding, and calls `dbdataNext()` to position on the first row. Normal page reads use `SELECT data FROM sqlite_dbpage(?) WHERE pgno=?`; function-like schema strings ending in `()` are treated as callbacks invoked as `name(?2)` and `name(0)` for page data and size.

`dbdataNext()` is the main parser. It loads pages in page-number order, skips missing or too-small pages, reads the b-tree page type at offset 100 for page 1 or offset 0 otherwise, clamps cell counts to a copy of SQLite's maximum-cell formula, and then either emits child pointers (`sqlite_dbptr`) or decodes record payload (`sqlite_dbdata`). For data records it handles leaf table pages, leaf index pages, and interior index pages with a child pointer prefix. It decodes payload size varints, optional intkey rowid, local payload size, overflow chain pages, record header size, serial types, and field data pointers.

`dbdataColumn()` returns the current page/cell/field/value for `sqlite_dbdata`, using field `-1` for intkey rowids. For `sqlite_dbptr`, it returns the parent page and either the right-child pointer or each cell child pointer. `dbdataRowid()` returns an internal incrementing rowid unrelated to source table rowids.

## State and Persistence Behavior

The module is read-only and creates no persistent tables. Cursor state is entirely in memory. Page buffers are allocated per loaded page and freed when moving to the next page or closing. Record payload buffers are retained and grown as needed, then freed on cursor reset/close. `DbdataTable.pStmt` caches one page-fetch statement across cursor resets to reduce prepare churn; if a second cursor has a statement while the table cache is occupied, the cursor statement is finalized.

The design intentionally tolerates corrupt content. It pads page and record buffers with `DBDATA_PADDING_BYTES`, clamps out-of-range varints and cell counts, substitutes benign zero/empty values if a field's bytes are truncated, stops following invalid/missing overflow chains, and skips pages that do not look parseable. Most corruption is represented as missing or partial rows instead of SQLite errors.

## Dependencies and Integration Points

The module depends on SQLite virtual table APIs, `sqlite_dbpage`, SQLite record-format constants, b-tree page layout, varint encoding, text encoding constants, and extension initialization conventions. It calls `sqlite3_vtab_config(db, SQLITE_VTAB_USES_ALL_SCHEMAS)` so the hidden `schema` column may target attached databases. It is compiled out when `SQLITE_OMIT_VIRTUALTABLE` is defined.

It integrates with recovery code by exposing low-level data through SQL. `sqlite_dbdata` can recover values from damaged tables even when normal b-tree traversal fails. `sqlite_dbptr` can reconstruct or inspect page graph relationships. The function-like schema mode lets recovery tooling provide alternate page sources, not only attached database names.

## Risks and Edge Cases

The parser manually mirrors SQLite file-format rules, so page-layout changes would require updates here. It assumes page sizes and offsets are sane enough after basic checks. It deliberately masks many corrupt conditions, which is useful for recovery but risky if callers expect complete or integrity-checked output. Rows may be omitted, values may be defaulted to zero or empty, and overflow payloads may be truncated without an error.

Integer and floating-point decoding relies on serial types and big-endian assembly. The double path copies the assembled 64-bit value into a `double`, which follows SQLite's stored IEEE representation but remains low-level and architecture-sensitive in appearance. `dbdataBestIndex()` assigns both schema and pgno arguments by position; bugs in constraint handling could bind page numbers incorrectly, but the `idxNum` bit protocol keeps the current mapping straightforward.

The hidden `schema` value can be treated as a SQL function name if it ends in `()`. This is powerful for recovery workflows but means callers should not pass untrusted arbitrary strings as schema selectors in contexts where preparing `SELECT <name>(...)` would be unsafe.

## Test Signals

The surrounding recover tests (`recover*.test`, `recover_common.tcl`, and related fault/corruption tests) are the likely consumers. Important signals include scans over normal databases, corrupt pages, overflow chains, attached schemas, one-page scans with `pgno=?`, child-pointer extraction, UTF-16 text decoding, and operation when `sqlite_dbpage` supplies missing or malformed pages.
