# sources/storage-engines/sqlite/ext/fts3/fts3Int.h

## Purpose
`fts3Int.h` is the private shared interface for SQLite's FTS3/FTS4 implementation. It normalizes compile-time feature flags, defines portable helper macros and scalar types for non-amalgamation builds, declares the core FTS table/cursor/expression/doclist/segment structures, and publishes cross-file prototypes used by the FTS3 tokenizer, expression parser, snippet/matchinfo code, write path, segment readers, auxiliary tables, and integrity checker.

## Important APIs, Types, And Functions
The header defines build and format constants such as `SQLITE_FTS3_MAX_EXPR_DEPTH`, `FTS3_MERGE_COUNT`, `FTS3_MAX_PENDING_DATA`, `FTS3_VARINT_MAX`, `FTS3_BUFFER_PADDING`, `FTS3_SEGDIR_MAXLEVEL`, `POS_COLUMN`, and `POS_END`. It also aliases `SQLITE_ENABLE_FTS4` to `SQLITE_ENABLE_FTS3` and disables FTS when virtual tables are omitted.

`Fts3Table` is the connection-level virtual-table object. It embeds `sqlite3_vtab`, database/table names, column metadata, notindexed flags, tokenizer pointer, external-content and languageid settings, statement caches, FTS3/FTS4 mode flags, page/node sizes, segment blob state, savepoint state, prefix-index definitions, pending-term hash tables, pending-data counters, previous-docid/langid tracking, and debug transaction fields.

`Fts3Cursor` is the per-query cursor object. It embeds `sqlite3_vtab_cursor` and tracks search strategy, EOF/seek flags, active SQLite statement, parsed expression tree, language id, deferred tokens, current doclist pointers, ordering, evaluation mode, row-size estimates, document counts, docid range constraints, and matchinfo buffer state.

The expression model is `Fts3Expr`, `Fts3Phrase`, and `Fts3PhraseToken`. Phrase tokens store parsed token text, prefix/first-position flags, and evaluation-time deferred-token or segment-reader state. Phrases cache merged doclists and OR-position state. Expression nodes form trees with types `FTSQUERY_NEAR`, `FTSQUERY_NOT`, `FTSQUERY_AND`, `FTSQUERY_OR`, and `FTSQUERY_PHRASE`.

Segment-reader contracts are represented by `Fts3SegFilter` and `Fts3MultiSegReader`. Filter flags include `FTS3_SEGMENT_REQUIRE_POS`, `FTS3_SEGMENT_IGNORE_EMPTY`, `FTS3_SEGMENT_COLUMN_FILTER`, `FTS3_SEGMENT_PREFIX`, `FTS3_SEGMENT_SCAN`, and `FTS3_SEGMENT_FIRST`. Special segment levels `FTS3_SEGCURSOR_PENDING` and `FTS3_SEGCURSOR_ALL` select pending terms or all persisted segments.

The prototype groups define the private FTS3 subsystem API: write/update and segment maintenance (`sqlite3Fts3UpdateMethod()`, pending flush/clear, optimize, reader creation/free, block reads, stat/docsize selectors, incremental merge), deferred-token helpers, segment-reader stepping, prepared-statement helper, varint/doclist/evaluator helpers from `fts3.c`, tokenizer initialization, snippet/offsets/matchinfo APIs, expression parsing/freeing, tokenize-vtab registration, unicode helpers, expression iteration, and integrity checking.

## Control Flow
This header does not execute code, but it defines the cross-module flow of the FTS subsystem. SQLite vtab callbacks in `fts3.c` allocate and populate `Fts3Table`/`Fts3Cursor`; write-side code updates pending-term hashes and segment tables; segment-reader code fills `Fts3MultiSegReader` objects; expression-parser code produces `Fts3Expr` trees; evaluator code traverses phrases and segment readers; snippet/matchinfo code consumes evaluator state through the declared APIs.

Conditional compilation shapes that flow. If FTS4 deferred tokens are disabled, deferred-token functions become no-op macros. If unicode support is disabled, unicode tokenizer helpers disappear. Test builds expose expression test interfaces and debug knobs. Non-amalgamation builds define SQLite-style scalar typedefs and macros that the amalgamation would normally provide.

## State And Persistence Behavior
`Fts3Table` is the primary in-memory owner for persistent FTS metadata and transient transaction state. It records which shadow tables exist, which prefix indexes are configured, how large pending-term buffers may grow before being flushed, and which language id the pending terms belong to. Its statement cache and segment blob handle are connection-local resources, not persisted state.

Persistent state is represented indirectly through the constants and APIs in this header: `%_segments` and `%_segdir` hold segment b-trees; `%_content` holds table content unless an external content table is configured; `%_docsize` and `%_stat` hold FTS4 size/statistics metadata. `FTS3_MERGE_COUNT`, `FTS3_SEGDIR_MAXLEVEL`, and pending-data limits constrain how in-memory terms become persistent segments and how those segments are merged.

`Fts3Cursor`, `Fts3Expr`, `Fts3Phrase`, `Fts3Doclist`, and `Fts3MultiSegReader` are transient query/evaluation state. They hold pointers into malloced buffers, segment-reader outputs, prepared statements, and deferred-token caches, so ownership cleanup must be coordinated between evaluator, cursor close, and expression free routines.

## Dependencies
The header depends on SQLite public or extension headers (`sqlite3.h`, optionally `sqlite3ext.h`), tokenizer definitions in `fts3_tokenizer.h`, FTS hash support in `fts3_hash.h`, and standard C headers. It also relies on SQLite compile-time feature macros and, outside the amalgamation, provides fallback definitions for `ALWAYS`, `NEVER`, `TESTONLY`, `FLEXARRAY`, integer typedefs, and fallthrough annotations.

## Integration Points
Every major FTS3 source file includes this header to share private structures and prototypes. It is the contract between the virtual-table front end (`fts3.c`), write path (`fts3_write.c`), tokenizers, expression parser, snippet/matchinfo module, auxiliary term table, unicode helpers, and test hooks.

For SQLite integration, the header preserves extension vs core behavior with `SQLITE_EXTENSION_INIT3` and feature guards. For FTS4 integration, it makes FTS4 an extension of the FTS3 implementation by enabling FTS3 whenever FTS4 is requested and by carrying FTS4-specific table fields such as `bFts4`, `bHasDocsize`, `bHasStat`, prefix indexes, and language id state.

## Risks And Edge Cases
Because this header exposes private structure layouts across many `.c` files, layout changes have a broad blast radius. Fields such as `Fts3Cursor.pStmt`, phrase doclist pointers, deferred-token pointers, and segment-reader buffers have implicit ownership rules that are not enforced by the type system.

Compile-time feature combinations are risky. Disabling virtual tables undefines FTS, disabling deferred tokens changes evaluator behavior through macros, and non-amalgamation builds rely on local definitions matching SQLite core semantics. Any mismatch in `SQLITE_CORE`, `SQLITE_ENABLE_FTS3`, or `SQLITE_ENABLE_FTS4` can produce missing symbols or inconsistent module registration.

Doclist and segment constants are persistence-sensitive. Changing `POS_COLUMN`, `POS_END`, varint limits, segment level layout, or merge count assumptions can break compatibility with existing FTS indexes or corrupt query interpretation. `assert_fts3_nc()` also distinguishes debug assertions that are valid only for non-corrupt databases from checks that must survive hostile on-disk data.

## Test Signals
Useful tests should compile FTS3/FTS4 in core and loadable-extension configurations, with and without unicode, ICU, deferred tokens, debug, and amalgamation builds. Runtime tests should exercise all public prototypes through SQL-visible behavior: updates and pending-term flushes, segment reads and merges, tokenizer setup, expression parsing, snippet/offsets/matchinfo, fts4aux scans, prefix indexes, language ids, and integrity checks.

Structure-contract tests are indirect: memory sanitizer and corruption tests are important because this header defines many pointer-bearing objects and varint/doclist traversal contracts. Compatibility tests should verify that persisted FTS3/FTS4 indexes remain readable across builds using this header.
