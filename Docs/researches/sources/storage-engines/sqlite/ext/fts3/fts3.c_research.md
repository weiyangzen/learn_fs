# sources/storage-engines/sqlite/ext/fts3/fts3.c

## Purpose
`fts3.c` is the central SQLite FTS3/FTS4 virtual-table implementation unit. It registers the `fts3` and `fts4` modules, parses virtual-table constructor options, declares the virtual table schema, creates and drops shadow tables, implements most read-side virtual-table methods, exposes the overloaded `snippet()`, `offsets()`, `matchinfo()`, and `optimize()` functions, and drives full-text query evaluation over FTS segment b-trees and doclists.

The file also documents and implements core FTS3 encodings: FTS3 little-endian varints, doclists, position lists, segment leaf/interior/root nodes, segment directories, merge-level behavior, and delete/update replacement semantics. Write-side mutation and low-level segment IO are mostly implemented in other FTS3 files, but this file owns the query planner interface, query cursor lifecycle, doclist merging, expression traversal, and extension initialization.

## Important APIs, Types, And Functions
The extension entry points are `sqlite3Fts3Init(sqlite3 *db)` and, for loadable builds, `sqlite3_fts3_init()`. `sqlite3Fts3Init()` registers `fts4aux`, built-in tokenizers, the tokenizer helper table, overloaded scalar functions, the `fts3` and `fts4` virtual-table modules, and the tokenize virtual table.

The `fts3Module` `sqlite3_module` table wires SQLite callbacks to local implementations: `fts3CreateMethod`, `fts3ConnectMethod`, `fts3BestIndexMethod`, `fts3OpenMethod`, `fts3CloseMethod`, `fts3FilterMethod`, `fts3NextMethod`, `fts3EofMethod`, `fts3ColumnMethod`, `fts3RowidMethod`, transaction callbacks, `fts3FindFunctionMethod`, `fts3RenameMethod`, `fts3ShadowName`, and `fts3IntegrityMethod`.

Constructor parsing is centered on `fts3InitVtab()`. It handles tokenizer arguments, FTS4-only options such as `matchinfo=fts3`, `prefix=`, `compress=`, `uncompress=`, `order=`, `content=`, `languageid=`, and `notindexed=`, builds the `Fts3Table` allocation, initializes pending-term hash tables for main and prefix indexes, prepares read/write expression lists, optionally creates shadow tables, and declares the vtab schema.

Utility APIs exported to sibling FTS3 files include `sqlite3Fts3PutVarint()`, `sqlite3Fts3GetVarint()`, `sqlite3Fts3GetVarintU()`, `sqlite3Fts3GetVarintBounded()`, `sqlite3Fts3GetVarint32()`, `sqlite3Fts3VarintLen()`, `sqlite3Fts3Dequote()`, `sqlite3Fts3ErrMsg()`, `sqlite3Fts3ReadInt()`, `sqlite3Fts3CreateStatTable()`, `sqlite3Fts3DoclistPrev()`, `sqlite3Fts3FirstFilter()`, `sqlite3Fts3EvalTestDeferred()`, `sqlite3Fts3EvalPhraseStats()`, `sqlite3Fts3EvalPhrasePoslist()`, `sqlite3Fts3MsrCancel()`, and `sqlite3Fts3EvalPhraseCleanup()`.

Segment-reader integration is exposed through `sqlite3Fts3SegReaderCursor()`. Internally, `fts3SegReaderCursor()` adds pending-term and persisted segment readers, uses `fts3SelectLeaf()` and `fts3ScanInteriorNode()` to narrow b-tree leaf ranges, and appends readers into `Fts3MultiSegReader`. `fts3TermSegReaderCursor()` chooses prefix-index readers when possible, falling back to the main index for exact or prefix scans.

Doclist and position-list manipulation is implemented by helpers such as `fts3PoslistCopy()`, `fts3ColumnlistCopy()`, `fts3ReadNextPos()`, `fts3PoslistMerge()`, `fts3PoslistPhraseMerge()`, `fts3PoslistNearMerge()`, `fts3DoclistOrMerge()`, `fts3DoclistPhraseMerge()`, `fts3TermSelectMerge()`, and `fts3TermSelectFinishMerge()`. These routines are the backbone of OR, phrase, prefix, and NEAR matching.

Full-text evaluation uses `fts3EvalStart()`, `fts3EvalAllocateReaders()`, `fts3EvalStartReaders()`, `fts3EvalPhraseStart()`, `fts3EvalPhraseLoad()`, `fts3EvalPhraseNext()`, `fts3EvalNextRow()`, `sqlite3Fts3EvalTestDeferred()`, `fts3EvalNearTest()`, and `fts3EvalNext()`. Matchinfo statistics are gathered through `fts3EvalGatherStats()`, `fts3EvalUpdateCounts()`, and `sqlite3Fts3EvalPhraseStats()`.

## Control Flow
Module initialization starts in `sqlite3Fts3Init()`: initialize optional tokenizer modules, register `fts4aux`, create a reference-counted tokenizer hash, insert tokenizer modules, install test hooks when enabled, register overloaded functions, then create `fts3`, `fts4`, and tokenize virtual-table modules. The `hashDestroy()` callback decrements and finally clears the shared tokenizer hash.

`CREATE VIRTUAL TABLE ... USING fts3/fts4` flows through `fts3CreateMethod()` into `fts3InitVtab(isCreate=1)`. The initializer parses module arguments, resolves external content columns if `content=` is used without explicit columns, creates a default `content` column if none are supplied, initializes the requested tokenizer or the `simple` tokenizer, parses prefix indexes, allocates one contiguous `Fts3Table` object, builds shadow-table SQL fragments, creates `%_content`, `%_segments`, `%_segdir`, and optional `%_docsize`/`%_stat`, records page size, and calls `sqlite3_declare_vtab()`. `xConnect` follows the same path without creating shadow tables and marks legacy non-FTS4 `%_stat` detection as unknown.

Query planning enters `fts3BestIndexMethod()`. It prefers `docid`/`rowid` equality, then usable `MATCH`, then full content scan. It also records hidden `languageid` and docid range constraints in high `idxNum` bits and can consume rowid ordering in either direction. If a usable `MATCH` is unavailable but present, it returns a very high estimated cost so SQLite avoids a plan that would later fail.

Query execution starts with `fts3FilterMethod()`. It clears any reused cursor, decodes `idxNum`, records docid bounds and requested order, and either prepares a content scan statement, prepares a seek statement for direct docid lookup, or parses the `MATCH` expression with `sqlite3Fts3ExprParse()` and calls `fts3EvalStart()`. `fts3NextMethod()` then advances either the prepared SQLite statement or the FTS expression evaluator. For full-text matches, rows initially carry only docid/position-list state; `fts3ColumnMethod()` lazily calls `fts3CursorSeek()` when user column values or snippet-like functions need the underlying content row.

Full-text startup allocates a `Fts3MultiSegReader` for each query token, optionally estimates token costs and defers expensive common tokens for FTS4, and starts each phrase either as an incremental phrase iterator or by fully loading and merging token doclists. Prefix queries may use configured prefix indexes when their length matches, may scan a longer prefix index plus the main term, or may scan the main index directly.

Expression iteration is recursive. `fts3EvalNextRow()` advances phrase, AND, NEAR, OR, and NOT nodes in docid order. For AND/NEAR, child iterators are synchronized to the same docid; NEAR is initially treated like AND. OR chooses the smaller next docid and advances duplicates on both sides. NOT advances the right side far enough to exclude matching left-side docids. `sqlite3Fts3EvalTestDeferred()` then seeks and tokenizes the current content row for deferred tokens and runs `fts3EvalTestExpr()` plus `fts3EvalNearTest()` to reject false positives and trim NEAR position lists for snippet/offset/matchinfo correctness.

Transaction flow uses `fts3BeginMethod()` to reset per-transaction counters and detect `%_stat`, `fts3SyncMethod()` to flush pending terms to segments and possibly run auto incremental merge, `fts3CommitMethod()` as a post-sync assertion/no-op, and `fts3RollbackMethod()`/`fts3RollbackToMethod()` to discard pending in-memory terms. `fts3SavepointMethod()` forces a flush by issuing a special insert into the virtual table unless the table is suppressing recursive savepoint behavior during rename.

## State And Persistence Behavior
Persistent FTS state lives in shadow tables named from the virtual table: `%_content` unless `content=` makes the table external-content, `%_segments`, `%_segdir`, optional FTS4 `%_docsize`, and optional `%_stat`. Segment data is an append/merge-oriented collection of immutable b-tree-like structures, and `%_segdir` stores roots and block ranges. Deletes and updates are represented by newer doclist entries that supersede older entries during query-time and merge-time doclist merging.

In-memory table state in `Fts3Table` includes tokenizer ownership, table/database names, column metadata, notindexed flags, content/languageid settings, prepared statement caches, page and node-size estimates, pending-term hash tables for each index, merge counters, an optional reusable seek statement, and a shared `%_segments` blob handle managed by sibling write/segment code. `fts3DisconnectMethod()` finalizes cached statements, closes tokenizer state, and frees allocated strings; `fts3DestroyMethod()` first drops shadow tables.

Cursor state in `Fts3Cursor` includes search strategy, EOF/seek flags, current statement, parsed query expression, language id, deferred token list, doclist buffers, docid bounds, direction, matchinfo state, average-row-size estimates, and current docid. The content row is not always loaded when a match is found; `isRequireSeek` delays `%_content` lookup until a column or auxiliary function needs it.

Doclists are delta-varint encoded and include position lists per document unless a bare docid list is explicitly used. Position lists use `POS_COLUMN` and `POS_END` sentinels and encode positions as delta-plus-two values. Much of the file assumes zero padding (`FTS3_BUFFER_PADDING`) after doclist buffers to simplify varint/terminator scans safely.

## Dependencies
This file depends on `fts3Int.h`, `fts3.h`, SQLite core/extension APIs, tokenizer modules, tokenizer/hash helpers, expression parsing, snippet/matchinfo helpers, write-side FTS3 functions, segment-reader implementations, and optional ICU/unicode/test modules. Key sibling APIs include `sqlite3Fts3UpdateMethod()`, `sqlite3Fts3PendingTermsFlush()`, `sqlite3Fts3PendingTermsClear()`, `sqlite3Fts3Optimize()`, segment-reader creation/stepping/freeing, `%_stat`/`%_docsize` selectors, deferred-token cache APIs, tokenizer initialization, and integrity checking.

Compile-time switches strongly shape behavior: `SQLITE_CORE`, `SQLITE_ENABLE_FTS3`, `SQLITE_ENABLE_FTS4`, `SQLITE_DISABLE_FTS4_DEFERRED`, `SQLITE_DISABLE_FTS3_UNICODE`, `SQLITE_ENABLE_ICU`, `SQLITE_TEST`, and `SQLITE_DEBUG`. The file includes debug-only corruption assertion plumbing through `sqlite3_fts3_may_be_corrupt` and `sqlite3Fts3Corrupt()`.

## Integration Points
SQLite integrates this file through the virtual-table API and extension initialization API. The hidden table-name column passes a typed `Fts3Cursor` pointer to overloaded functions; `snippet()`, `offsets()`, `matchinfo()`, and `optimize()` validate that pointer with `sqlite3_value_pointer(..., "fts3cursor")` before operating on the current match.

The write path is delegated to `sqlite3Fts3UpdateMethod()` and segment maintenance functions in sibling files, but this file decides when pending terms are flushed, when auto incremental merge is attempted, when savepoints force flushes, and how rename/drop operations affect shadow tables. Integrity checks call `sqlite3Fts3IntegrityCheck()` and translate failures into SQLite `integrity_check` diagnostics.

`fts4aux` depends on this file's segment-reader and varint/doclist helpers. Snippet and matchinfo code depend on the evaluator's position-list state, deferred-token handling, and `sqlite3Fts3EvalPhrasePoslist()`/`sqlite3Fts3EvalPhraseStats()` interfaces.

## Risks And Edge Cases
The main correctness risk is malformed on-disk FTS data. The file performs many corruption checks for impossible prefix lengths, b-tree heights, child ordering, invalid column markers, missing content rows, and inconsistent restart positions, but several low-level doclist scans still rely on padding and format invariants. Corruption handling must consistently return `SQLITE_CORRUPT_VTAB` or related codes without overreading.

Virtual-table recursion is guarded by `Fts3Table.bLock`; missing or misplaced lock increments around internal SQL can lead to recursive use errors or planner failures. External-content tables deliberately disable deferred-token optimization because index and content rows may not be synchronized.

Prefix and descending-order indexes make doclist sizing and merge logic subtle. The code adds varint padding in several output allocations because descending deltas or negative first docids can require larger encodings after merge. Changing docid ordering, position-list trimming, or OR/NEAR restart behavior can silently break snippets, offsets, and matchinfo even if rowid result sets look correct.

`fts3InitVtab()` has many constructor option interactions: `content=` suppresses compression hooks, `compress` and `uncompress` must appear together, `notindexed=` must match a column, and `languageid=` may remove a column imported from an external content table. Memory ownership crosses tokenizer objects, option strings, copied column arrays, and one large `Fts3Table` allocation; error paths must preserve those ownership rules.

## Test Signals
Good behavioral tests should cover FTS3 and FTS4 creation, connect, rename, drop, shadow-table creation, external-content tables, prefix indexes, `languageid=`, `notindexed=`, `order=desc`, `matchinfo=fts3`, compression/uncompression option validation, and tokenizer selection. Query tests should include docid lookup, full scans with rowid ranges, MATCH on all columns and a single column, phrase queries, prefix queries with and without prefix indexes, NEAR chains, AND/OR/NOT trees, first-token `^` filters, deferred-token cases, and descending output.

Persistence tests should verify pending-term flushing on commit/savepoint, rollback clearing, auto incremental merge triggers, optimize results, integrity-check diagnostics, and corruption handling for malformed segment roots/doclists/column markers. Auxiliary-function tests should validate `snippet()`, `offsets()`, and `matchinfo()` after OR/NEAR/deferred queries, because those depend on the evaluator retaining and trimming correct per-row position lists.
