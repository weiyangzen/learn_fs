# sources/storage-engines/sqlite/ext/fts5/fts5_main.c

## Purpose

`fts5_main.c` is the primary SQLite virtual table module implementation for FTS5. It registers the `fts5` module, wires SQLite virtual table callbacks to the FTS5 config, expression, index, storage, tokenizer, vocab, and auxiliary-function subsystems, and exposes the public `fts5_api`/`Fts5ExtensionApi` surfaces used by extensions. It owns query planning, cursor lifecycle, MATCH execution, rank sorting, column materialization, update handling, transaction/savepoint callbacks, extension API dispatch, tokenizer registration, and SQL helper functions such as `fts5()`, `fts5_source_id()`, `fts5_locale()`, and `fts5_insttoken()`.

## Important APIs, types, and functions

Key types are `Fts5Global`, `Fts5FullTable`, `Fts5Cursor`, `Fts5Sorter`, `Fts5Auxiliary`, `Fts5TokenizerModule`, and `Fts5Auxdata`. `Fts5Global` is connection-scoped state: the public `fts5_api`, registered tokenizers, registered auxiliary functions, open cursor list, and the randomized locale blob header. `Fts5FullTable` extends the public `Fts5Table` with `Fts5Storage`, connection global state, sorted-query cursor state, and debug transaction bookkeeping. `Fts5Cursor` carries a virtual-table cursor plan, rowid bounds, expression tree, content statement, sorter, rank function state, auxiliary data, and cached match-instance arrays.

Module setup is centered on `fts5Init()`, which creates the `sqlite3_module`, initializes index/expression/aux/tokenizer/vocab subsystems, registers SQL functions, and installs the module destructor. `sqlite3_fts_init()`, `sqlite3_fts5_init()`, or `sqlite3Fts5Init()` call it depending on loadable-extension versus core builds. `fts5InitVtab()`, `fts5CreateMethod()`, and `fts5ConnectMethod()` parse table options, load tokenizers, open index/storage handles, declare the virtual schema, load config, and set virtual-table safety flags.

Query planning is handled by `fts5BestIndexMethod()`, which encodes MATCH/rank/rowid/LIKE/GLOB constraints into `idxStr`, stores ORDER BY flags in `idxNum`, estimates cost/rows, and marks rowid equality as unique. Runtime query setup is in `fts5FilterMethod()`: it decodes `idxStr`, extracts locale-wrapped MATCH text, builds or combines `Fts5Expr` objects, applies rowid bounds, chooses scan/rowid/MATCH/sorted/special plans, and opens content statements or expression iterators. Cursor movement is split across `fts5CursorFirst()`, `fts5CursorFirstSorted()`, `fts5SorterNext()`, `fts5CursorReseek()`, and `fts5NextMethod()`.

Writes enter through `fts5UpdateMethod()`, with helpers `fts5SpecialInsert()`, `fts5SpecialDelete()`, `fts5StorageInsert()`, and `fts5ContentlessUpdate()`. Transaction entry points are `fts5BeginMethod()`, `fts5SyncMethod()`, `fts5CommitMethod()`, `fts5RollbackMethod()`, `fts5SavepointMethod()`, `fts5ReleaseMethod()`, and `fts5RollbackToMethod()`. `sqlite3Fts5FlushToDisk()` trips cursors and delegates persistence to storage.

The extension API is the static `sFts5Api` object. It maps xUserData, xColumnCount, xRowCount, xColumnTotalSize, xTokenize/xTokenize_v2, xPhraseCount, xPhraseSize, xInstCount, xInst, xRowid, xColumnText, xColumnSize, xQueryPhrase, xSetAuxdata/xGetAuxdata, phrase iterators, xQueryToken, xInstToken, and xColumnLocale onto cursor and storage internals. Auxiliary SQL dispatch uses `fts5CreateAux()`, `fts5FindFunctionMethod()`, `fts5ApiCallback()`, and `fts5ApiInvoke()`. Tokenizer registration uses `fts5CreateTokenizer()`, `fts5CreateTokenizer_v2()`, `fts5FindTokenizer()`, `fts5FindTokenizer_v2()`, `fts5LoadTokenizer()`, and wrapper adapters between v1 and v2 tokenizer APIs.

## Control flow

Creation/connect allocates `Fts5FullTable`, parses config, opens the index and storage subsystems, declares the virtual table, and loads the config cookie. Query planning first scans constraints for MATCH-like clauses, rank MATCH, rowid equality/ranges, and tokenizer-supported LIKE/GLOB pattern matches. `xFilter` then converts those encoded constraints into either a full text expression, a special internal query (`MATCH '*reads'` or `MATCH '*id'`), a rowid lookup, or a content scan.

Normal MATCH execution initializes an `Fts5Expr` iterator against `Fts5Index` and advances it row by row. Content is lazy: cursor flags such as `FTS5CSR_REQUIRE_CONTENT`, `FTS5CSR_REQUIRE_DOCSIZE`, `FTS5CSR_REQUIRE_INST`, and `FTS5CSR_REQUIRE_POSLIST` indicate which derived row data must be loaded or recomputed. `xColumn` fetches the table-name hidden column as a cursor id, evaluates rank through the configured auxiliary function, or seeks into storage for user columns. For `ORDER BY rank`, `fts5CursorFirstSorted()` prepares a recursive SELECT over the same virtual table that materializes `(rowid, rank)` sorted by rank; the outer cursor then reads pre-sorted rows and position-list blobs from a `Fts5Sorter`.

Updates branch by operation shape: delete has one argument, insert has a NULL old rowid, update has integer old/new rowids, and special inserts use the hidden table-name column. Regular writes call storage to delete old index/content/docsize rows and insert new content/index/docsize rows. Contentless tables restrict UPDATE and DELETE unless `contentless_delete=1` semantics permit the operation; updates that touch only unindexed columns can be content-only operations for contentless-unindexed tables.

## State and persistence behavior

Persistent data is not written directly by this file; it is delegated to `fts5_storage.c` and `fts5_index.c`. This file controls when pending index state is flushed, reset, or invalidated. `xSync`, savepoint creation, and some release paths flush pending terms and totals through `sqlite3Fts5FlushToDisk()`. Rollback and rollback-to discard cached index/storage state and reset config page-size state. `fts5TripCursors()` marks active MATCH cursors for reseek before writes or flushes so reads do not continue on stale index iterators.

Locale state is transiently stored in `Fts5Config.t.pLocale/nLocale` around tokenization. `fts5_locale()` returns a blob with a connection-randomized header, locale text, a nul separator, and text; `sqlite3Fts5IsLocaleValue()` and `sqlite3Fts5DecodeLocaleValue()` identify and unpack these values only for the owning `Fts5Global` header. `fts5_insttoken()` marks a query value with a subtype that enables prefix token retention for xInstToken.

Auxiliary data is cursor-scoped and auxiliary-function-scoped via `Fts5Auxdata`; destructors run when the cursor is reset or closed. Tokenizer and auxiliary registrations are connection-scoped and freed by `fts5ModuleDestroy()`.

## Dependencies and integration points

This file depends on `fts5Int.h` internals and calls into config (`sqlite3Fts5Config*`), index (`sqlite3Fts5Index*`), storage (`sqlite3Fts5Storage*`), expression (`sqlite3Fts5Expr*`), tokenizer (`sqlite3Fts5Tokenize`, tokenizer init/pattern helpers), aux (`sqlite3Fts5AuxInit`), and vocab (`sqlite3Fts5VocabInit`) modules. It integrates tightly with SQLite virtual table APIs: `sqlite3_create_module_v2`, `sqlite3_vtab_config`, `sqlite3_index_info`, `xFindFunction`, `sqlite3_overload_function`, subtypes, pointer binding, and shadow-table naming/integrity callbacks.

## Risks and edge cases

High-risk areas are recursive virtual-table use for rank sorting, cursor reseek after writes, locale blob identification tied to connection-local random headers, and `idxStr` encoding/decoding consistency between `xBestIndex` and `xFilter`. Contentless/contentless-delete rules are subtle and must preserve index correctness without stored content. `sqlite3_value_nochange()` handling depends on storage saved-row behavior to preserve unmodified values and locales. Detail modes other than `full` require reconstructing position lists from content, which is impossible for contentless tables and therefore returns empty lists. Corruption handling deliberately converts missing content rows, malformed position/docsize state, and impossible column positions into `FTS5_CORRUPT` paths.

## Test signals

The file has extensive assert-based transaction-state checks under `SQLITE_DEBUG`, special test/debug directives such as `prefix-index`, public integrity plumbing via `xIntegrity`, and SQL helper functions that are exercised by Tcl and FTS5 extension tests. `SQLITE_FTS5_ENABLE_TEST_MI` can register the test `matchinfo()` implementation. The companion Tcl/test files in this work item exercise the extension API, tokenizer v1/v2 bridging, locale propagation, matchinfo compatibility, tokenization output, corruption toggles, and dropping corrupt FTS5 tables.
