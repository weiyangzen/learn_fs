# sources/storage-engines/sqlite/ext/fts3/fts3_write.c

## Purpose
`fts3_write.c` is the write-side and segment-maintenance implementation for SQLite FTS3/FTS4 virtual tables. It handles `xUpdate()` inserts, deletes, updates, special maintenance commands, pending-term accumulation, full and incremental segment merges, segment b-tree construction, docsize/stat maintenance, integrity checking, and some segment-reader helpers also used by query code in `fts3.c`.

The file is compiled when FTS3 is enabled. It is tightly coupled to the FTS shadow-table schema: `%_content`, `%_segments`, `%_segdir`, `%_docsize`, and `%_stat`.

## Important APIs, Types, And Functions
Core transient types are `PendingList`, `Fts3DeferredToken`, `Fts3SegReader`, `SegmentWriter`, and `SegmentNode`. Incremental merge adds `Blob`, `NodeReader`, `NodeWriter`, and `IncrmergeWriter`.

Statement plumbing is centralized in `sqlite3Fts3PrepareStmt()`, `fts3SqlStmt()`, and `fts3SqlExec()`. `fts3SqlStmt()` maps `SQL_*` constants to cached prepared statements for all shadow-table operations and binds optional parameters.

Update entry points include `sqlite3Fts3UpdateMethod()`, `fts3InsertData()`, `fts3InsertTerms()`, `fts3DeleteTerms()`, `fts3DeleteByRowid()`, `fts3DeleteAll()`, `fts3InsertDocsize()`, and `fts3UpdateDocTotals()`. `fts3SpecialInsert()` dispatches hidden-column commands: `optimize`, `rebuild`, `integrity-check`, `merge=A,B`, `automerge=X`, and `flush`, plus debug/test commands.

Pending-term and doclist construction flows through `fts3PendingTermsDocid()`, `fts3PendingTermsAdd()`, `fts3PendingTermsAddOne()`, `fts3PendingListAppend()`, and `sqlite3Fts3PendingTermsFlush()`. These functions tokenize content, populate per-index hash tables, and flush pending lists into segment b-trees.

Segment readers and writers include `sqlite3Fts3ReadBlock()`, `sqlite3Fts3SegmentsClose()`, `sqlite3Fts3SegReaderNew()`, `sqlite3Fts3SegReaderPending()`, `fts3SegReaderNext()`, `fts3SegReaderFirstDocid()`, `fts3SegReaderNextDocid()`, `sqlite3Fts3SegReaderStart()`, `sqlite3Fts3SegReaderStep()`, and `sqlite3Fts3SegReaderFinish()`. Writer functions include `fts3SegWriterAdd()`, `fts3SegWriterFlush()`, `fts3NodeAddTerm()`, `fts3NodeWrite()`, `fts3WriteSegment()`, and `fts3WriteSegdir()`.

Merge and maintenance APIs include `fts3SegmentMerge()`, `fts3AllocateSegdirIdx()`, `fts3PromoteSegments()`, `sqlite3Fts3Incrmerge()`, `fts3IncrmergeWriter()`, `fts3IncrmergeAppend()`, `fts3IncrmergeChomp()`, `fts3IncrmergeHintLoad()`, `fts3IncrmergeHintStore()`, `fts3DoOptimize()`, `fts3DoRebuild()`, `sqlite3Fts3Optimize()`, and `sqlite3Fts3IntegrityCheck()`.

## Control Flow
Normal insert/update/delete work enters through `sqlite3Fts3UpdateMethod()`. Special hidden-column inserts are intercepted first. Otherwise the method allocates document-size delta arrays, obtains a write lock on `%_segdir`, handles rowid conflict behavior, deletes any old row, inserts the new content row if needed, tokenizes indexed columns into pending-term hashes, writes `%_docsize`, updates `%_stat` totals for FTS4, closes any open segment blob handle, and returns the accumulated SQLite status.

Pending terms are ordered by docid/language/index constraints. `fts3PendingTermsDocid()` flushes if docids go backwards, delete/insert ordering would become ambiguous, language id changes, or the pending memory budget is exceeded. `sqlite3Fts3PendingTermsFlush()` calls `fts3SegmentMerge()` with `FTS3_SEGCURSOR_PENDING` for every main/prefix index, then clears the pending hashes.

Segment writing is prefix-compressed. Leaf nodes contain a height byte, term prefix/suffix varints, term suffix bytes, doclist size, and doclist bytes. `SegmentWriter` writes full leaf nodes to `%_segments`, builds an in-memory interior `SegmentNode` tree, and finally writes a `%_segdir` row with root data. Small segments can live entirely in `%_segdir.root`; larger segments use `%_segments` blocks for leaves and interior nodes.

Segment reading advances a collection of `Fts3SegReader` objects over pending hashes or persisted segment b-trees. `sqlite3Fts3SegReaderStep()` sorts readers by term, merges identical-term doclists, applies column filtering and prefix/exact/scan filters, and emits either a direct doclist pointer or a merged buffer. Incremental doclist reading uses `sqlite3_blob` handles and chunk thresholds to avoid loading large nodes unless necessary.

Full merge (`fts3SegmentMerge()`) opens readers over a level or all levels, emits merged doclists into a new `SegmentWriter`, deletes obsolete segment blocks and segdir entries, flushes the writer to the next level, and may promote smaller higher-level segments down to the new level for balance. `fts3DoOptimize()` flushes pending data and merges every language/index combination into one segment where possible.

Incremental merge (`sqlite3Fts3Incrmerge()`) repeatedly selects a level with enough segments or resumes a stored hint from `%_stat`. It opens the oldest segments, creates or appends to an appendable output segment, writes only a bounded number of leaf pages, then either deletes fully consumed input segments or truncates partially consumed ones so already copied terms are not duplicated. Hints store unfinished `(absolute-level, input-count)` pairs as varints in `%_stat`.

Integrity checking computes a checksum by scanning the FTS index and another checksum by tokenizing the content rows, including prefix indexes and language ids. A mismatch produces `FTS_CORRUPT_VTAB` through `fts3DoIntegrityCheck()` or `*pbOk = 0` through `sqlite3Fts3IntegrityCheck()`.

## State And Persistence Behavior
In-memory state includes cached prepared statements in `Fts3Table.aStmt`, pending-term hash tables in each `Fts3Index`, pending byte counters, last docid/language/delete metadata, reusable `%_segments` blob handles, query/merge buffers, and deferred-token doclists on cursors.

Persistent state is stored in FTS shadow tables. `%_content` stores user column content unless the table is external-content/contentless. `%_segments` stores segment blocks keyed by blockid, including NULL block markers used to reserve appendable incremental-merge space. `%_segdir` maps absolute levels and indexes to segment block ranges and root blobs. `%_docsize` stores per-row token counts. `%_stat` stores total document statistics, incremental-merge hints, and automerge settings.

Absolute segment levels encode language id, main/prefix index id, and relative level: `((iLangid * nIndex + iIndex) * FTS3_SEGDIR_MAXLEVEL) + iLevel`. This encoding is fundamental to merges, language filtering, and prefix-index separation.

The code carefully closes `p->pSegments` before returning to SQLite callers so blob handles do not hold database locks longer than a virtual-table method. Many functions propagate `SQLITE_NOMEM`, IO errors, or `FTS_CORRUPT_VTAB` and leave transaction rollback to SQLite.

## Dependencies
The file depends on `fts3Int.h`, SQLite core APIs, tokenizer APIs, varint/doclist helpers from the FTS3 subsystem, FTS hash-table helpers, and build-time macros such as `SQLITE_ENABLE_FTS3`, `SQLITE_TEST`, `SQLITE_DISABLE_FTS4_DEFERRED`, `FTS3_LOG_MERGES`, and debug/assertion macros.

Important integration points outside this file include FTS3 table setup/destruction code, query evaluation in `fts3.c`, tokenizer modules, FTS4 stat/docsize helpers, and tests that exercise special inserts and corruption handling.

## Risks And Edge Cases
The largest risk is corruption handling in compact binary formats. Segment nodes, doclists, root blobs, varints, and `%_segdir.end_block` text/int dual encoding are all parsed manually. The code adds padding and many bounds checks, but malformed databases still exercise subtle integer, prefix-compression, and incremental-read paths.

Merge logic is stateful and persistent. Incorrect idx repacking, segment truncation, appendable block reservation, promotion, or hint handling can create duplicate terms, lost terms, leaked segment blocks, or future corruption. The `p->bIgnoreSavepoint` window in segdir repacking is also a delicate integration point with SQLite savepoint behavior.

External-content tables alter assumptions: content rows may not be stored in `%_content`, emptiness cannot be inferred the same way, and rebuild/integrity depend on reading the external source. Rowid/docid alias conflicts and `ON CONFLICT REPLACE` handling are another important edge.

Tokenizer behavior is trusted for non-negative positions and non-empty tokens. Tokenizers returning invalid positions or tokens cause `SQLITE_ERROR`; tokenizer OOM/IO errors propagate.

## Test Signals
High-value tests include insert/update/delete with explicit rowid and docid aliases; REPLACE conflict handling; external-content rebuilds; language-id isolation; prefix indexes; `order=desc`; docsize/stat correctness; pending flush at memory and docid ordering boundaries; optimize and full merge; incremental merge continuation across transactions; automerge persistence; corrupt node/doclist/root/end-block inputs; deferred-token query behavior; and integrity-check mismatch detection.

Existing signals are likely in SQLite FTS3/FTS4 test suites, `fts3.test`, corruption tests, incremental merge tests, optimize/rebuild/integrity command tests, and coverage tooling such as `ext/fts3/tool/fts3cov.sh`.
