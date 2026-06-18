# sources/storage-engines/sqlite/ext/fts5/fts5.h

## Purpose
`fts5.h` declares the public extension interfaces for SQLite FTS5. It lets applications register custom auxiliary functions and custom tokenizers, and it defines the callback tables that FTS5 passes to those extensions at runtime.

The header is ABI-facing: it contains forward declarations, function-pointer typedefs, versioned API structs, tokenizer structs, and tokenization flags. It includes `sqlite3.h` and wraps declarations in `extern "C"` for C++ consumers.

## Important APIs, Types, And Functions
`fts5_extension_function` is the signature for auxiliary SQL functions registered with FTS5. It receives an `Fts5ExtensionApi`, an `Fts5Context`, a SQLite result context, and trailing SQL values.

`Fts5PhraseIter` is an opaque iterator payload used by phrase-instance and phrase-column iteration APIs. Applications allocate it but must not inspect or mutate the fields directly.

`Fts5ExtensionApi` is the auxiliary-function callback table. Version 4 includes row/column metadata (`xColumnCount`, `xRowCount`, `xColumnTotalSize`, `xColumnSize`, `xColumnText`, `xColumnLocale`), query metadata (`xPhraseCount`, `xPhraseSize`, `xQueryToken`), match-instance APIs (`xInstCount`, `xInst`, `xInstToken`, `xPhraseFirst`, `xPhraseNext`, `xPhraseFirstColumn`, `xPhraseNextColumn`), row identity (`xRowid`), tokenizer access (`xTokenize`, `xTokenize_v2`), phrase query execution (`xQueryPhrase`), and per-query auxiliary cache (`xSetAuxdata`, `xGetAuxdata`).

`Fts5Tokenizer` is an opaque tokenizer instance. `fts5_tokenizer_v2` is the preferred tokenizer module interface with `iVersion`, `xCreate`, `xDelete`, and locale-aware `xTokenize`. `fts5_tokenizer` is the legacy interface without `iVersion` and without locale arguments.

Tokenization flags are `FTS5_TOKENIZE_QUERY`, `FTS5_TOKENIZE_PREFIX`, `FTS5_TOKENIZE_DOCUMENT`, and `FTS5_TOKENIZE_AUX`. Token callback flags include `FTS5_TOKEN_COLOCATED` for synonyms at the same token position.

`fts5_api` is the registration/retrieval table. It supports `xCreateTokenizer`, `xFindTokenizer`, `xCreateFunction`, and version-3 additions `xCreateTokenizer_v2` and `xFindTokenizer_v2`.

## Control Flow
Extensions do not instantiate these structs directly except for tokenizer modules. At initialization time, an application obtains `fts5_api` from SQLite's FTS5 extension mechanism, then registers tokenizers or auxiliary functions. During MATCH queries or auxiliary function calls, FTS5 invokes the registered callbacks and supplies an `Fts5ExtensionApi` plus an `Fts5Context`.

Auxiliary functions call `Fts5ExtensionApi` methods to inspect the current row, current query, phrase instances, column text, tokenizer output, and cached per-query state. Some methods can trigger internal scans, especially phrase queries, instance enumeration on reduced-detail tables, and token retrieval for prefix matches.

Tokenizer control flow starts with `xCreate()` when FTS5 needs a tokenizer instance, then repeated `xTokenize()` calls for document indexing, query parsing, prefix query parsing, or auxiliary tokenization. The tokenizer reports tokens by invoking the provided `xToken()` callback in input order and returns either `SQLITE_OK`, the callback's error code, or another SQLite error code. `xDelete()` is called once for each successfully created tokenizer instance.

## State And Persistence Behavior
This header itself stores no state and writes no data. It defines contracts for FTS5-owned state and extension-owned state.

Auxiliary data managed by `xSetAuxdata()`/`xGetAuxdata()` is scoped to a single MATCH query and a single auxiliary function. Replacing or query cleanup invokes the registered destructor unless the value is cleared with `xGetAuxdata(..., bClear!=0)`.

Tokenizer instances are extension-owned objects returned by `xCreate()` and later destroyed by `xDelete()`. Tokenizers may maintain their own configuration and locale behavior, but token text passed to callbacks is consumed by FTS5 according to the callback contract.

Persistent FTS index contents are affected indirectly by tokenizer output during `FTS5_TOKENIZE_DOCUMENT`. Changing tokenizer normalization, synonym emission, locale handling, or colocated token behavior can change indexed terms and therefore query compatibility with existing databases.

## Dependencies
The only direct include is `sqlite3.h`. The API depends on SQLite result/value types, SQLite integer types, SQLite error codes, and FTS5's virtual-table/runtime implementation that fills these callback tables.

## Integration Points
Auxiliary functions integrate through `fts5_api.xCreateFunction()` and are later found through FTS5's virtual-table `xFindFunction()` path. Tokenizers integrate through `xCreateTokenizer()` or `xCreateTokenizer_v2()` and are referenced by FTS5 table definitions and tokenizer lookup APIs.

The header explicitly documents behavior for `detail=none`, `detail=column`, contentless tables, `columnsize=0`, `tokendata=1`, `fts5_locale()`, prefix-token instance lookup, `insttoken`, and synonym strategies. These are key compatibility points between extension code and FTS5 storage/query internals.

## Risks And Edge Cases
This is a C ABI contract, so struct versioning matters. Callers must check `iVersion` before using version-gated fields. Setting tokenizer methods to NULL is undefined behavior. Legacy and v2 tokenizer APIs differ in locale support and registration/retrieval ownership.

Several APIs return pointers to FTS5-owned buffers rather than copies. Extension code must treat returned column text, query tokens, instance tokens, and locale strings as transient and must not write through them. Range errors are reported as `SQLITE_RANGE` for invalid columns, phrase indexes, instance indexes, or token indexes.

Performance traps are prominent: `xInstCount`, `xInst`, phrase iteration, and token retrieval may be slow for `detail=none`, `detail=column`, contentless tables, and prefix-token queries unless `insttoken` support is enabled. Tokenizers that emit synonyms in both query and document modes can work but waste CPU or disk. Misusing `FTS5_TOKEN_COLOCATED` as the first token is an error.

## Test Signals
Good tests register an auxiliary function that exercises all available `Fts5ExtensionApi` methods by version, validates auxdata destructor behavior, checks range errors, and compares phrase/column iteration order. Tokenizer tests should cover legacy and v2 registration, locale propagation, all tokenization flags, callback error propagation, synonyms with `FTS5_TOKEN_COLOCATED`, prefix queries, `tokendata=1`, contentless tables, and reduced-detail tables.
