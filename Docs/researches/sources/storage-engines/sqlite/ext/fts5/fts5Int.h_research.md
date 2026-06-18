# sources/storage-engines/sqlite/ext/fts5/fts5Int.h

## Purpose
`fts5Int.h` is the private coordination header for SQLite FTS5. It defines the shared scalar aliases, portability macros, constants, opaque type declarations, core structs, and cross-module function prototypes used by the FTS5 virtual table implementation. It is not a public API header; it binds together config parsing, buffer/poslist helpers, index access, virtual table storage, expression evaluation, hash accumulation, tokenizers, auxiliary functions, vocabulary tables, and Unicode helpers.

## Important APIs, types, and constants
- Basic aliases `u8`, `u16`, `u32`, `u64`, `i16`, and `i64` are provided for non-amalgamation builds, along with `ArraySize`, `ALWAYS`, `NEVER`, `MIN`, `MAX`, `FLEXARRAY`, and `UNUSED_PARAM` helpers.
- Limits and defaults include `FTS5_MAX_TOKEN_SIZE` at 32768 bytes, `FTS5_MAX_PREFIX_INDEXES` at 31, `FTS5_MAX_SEGMENT` at 2000, `FTS5_DEFAULT_NEARDIST` at 10, and `FTS5_DEFAULT_RANK` as `bm25`.
- `Fts5Config` is the central table configuration object. It stores database/table identity, column names, unindexed column flags, tokenizer state, prefix indexes, content mode, detail mode, locale/tokendata flags, config-table values such as page size and merge settings, rank function configuration, and error-message plumbing.
- `Fts5TokenizerConfig` abstracts tokenizer v1/v2 state, arguments, pattern mode, and current locale.
- `Fts5Buffer`, `Fts5PoslistReader`, `Fts5PoslistWriter`, and `Fts5Termset` define the shared buffer and position-list utilities implemented in `fts5_buffer.c`.
- `Fts5Index`, `Fts5IndexIter`, query flags, and write/read/sync/merge/integrity prototypes define the contract to `fts5_index.c`.
- `Fts5Table` maps the SQLite virtual table object to an FTS5 config and index.
- `Fts5Hash` prototypes define the transient term hash used before flushing postings to `%_data`.
- `Fts5Storage` prototypes define the persistence contract for `%_content`, `%_docsize`, `%_config`, and related rebuild/merge operations.
- `Fts5Expr`, `Fts5ExprNode`, `Fts5ExprPhrase`, `Fts5ExprNearset`, `Fts5Token`, and parse callbacks define the query-expression parse/evaluation boundary.
- Tokenizer, auxiliary, vocab, and Unicode prototypes make this header the single internal dispatch surface for module initialization.

## Control flow and integration
The header is organized by module interface. `fts5_main.c` and storage code parse a table declaration with `sqlite3Fts5ConfigParse()`, declare a virtual table schema, load tokenizers, open storage/index handles, and use `sqlite3Fts5IndexWrite()` plus `sqlite3Fts5Storage...()` functions for DML. Query planning builds `Fts5Expr` objects with `sqlite3Fts5ExprNew()` or `sqlite3Fts5ExprPattern()`, then iterates them through `sqlite3Fts5ExprFirst()`, `sqlite3Fts5ExprNext()`, `sqlite3Fts5ExprEof()`, and `sqlite3Fts5ExprRowid()`. Auxiliary functions access phrase counts, position lists, query tokens, and inst-token data through the expression APIs declared here.

## State and persistence behavior
This header does not persist state itself, but it defines all structs that carry persistent-table metadata and transient query/index state. `Fts5Config` mirrors both `CREATE VIRTUAL TABLE` options and runtime values loaded from `%_config`. The index/storage APIs declared here are responsible for writing postings, averages, config values, content rows, docsize rows, deletes, merges, rollbacks, and integrity checks. The hash and buffer APIs define transient in-memory state that is flushed or discarded by index sync/rollback paths.

## Dependencies
It includes `fts5.h` and `sqlite3ext.h`, then uses SQLite extension APIs, SQLite allocation APIs, varints, statements, virtual-table structs, and tokenizer/extension-function types. Build-time dependencies include generated parser and Unicode modules through prototypes elsewhere. Non-amalgamation builds receive local fallback typedefs and macros normally provided by SQLite internal headers.

## Risks and edge cases
- Because this is the internal ABI across FTS5 modules, changes to struct layout or prototype semantics can silently break multiple C files.
- `Fts5Config` contains ownership-sensitive pointers: tokenizer objects, `azCol`, `abUnindexed`, prefix arrays, SQL fragments, and rank strings must be freed consistently by `sqlite3Fts5ConfigFree()`.
- `FTS5_CURRENT_VERSION` and `FTS5_CURRENT_VERSION_SECUREDELETE` gate file-format compatibility; mismatched changes can produce unreadable indexes or bad upgrade behavior.
- Query flags share one bit namespace between public index-query behavior and internal skip/no-output behavior; collisions are explicitly avoided by this header.
- Detail modes, content modes, locale, tokendata, and contentless-delete options strongly affect downstream invariants. Callers must check the defined constants instead of assuming full-detail, content-bearing tables.

## Test signals
Useful tests should cover non-amalgamation builds, configuration combinations, tokenizer v1/v2 loading, detail modes, prefix-index limits, secure-delete format loading, contentless-delete/contentless-unindexed paths, expression parsing and iteration APIs, hash write/query/scan APIs, storage rollback/sync, and auxiliary APIs that depend on expression metadata.
