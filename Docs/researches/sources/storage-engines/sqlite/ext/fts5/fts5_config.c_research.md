# sources/storage-engines/sqlite/ext/fts5/fts5_config.c

## Purpose
`fts5_config.c` parses FTS5 virtual-table declarations, manages `Fts5Config` lifetime, declares the SQLite virtual table schema, tokenizes text through the configured tokenizer, parses rank specifications, applies `%_config` values, and loads persistent configuration from the `%_config` shadow table.

## Important APIs and functions
- `sqlite3Fts5ConfigParse()` builds an `Fts5Config` from xCreate/xConnect arguments.
- `sqlite3Fts5ConfigFree()` releases tokenizer instances, tokenizer args, names, columns, prefix arrays, rank strings, content SQL fragments, and the config object.
- `sqlite3Fts5ConfigDeclareVtab()` constructs the hidden-column virtual-table schema.
- `sqlite3Fts5Tokenize()` lazily loads the tokenizer and dispatches to tokenizer v1 or v2, passing locale to v2.
- `sqlite3Fts5ConfigParseRank()` validates strings like `bm25(1.0, 'x')` and splits function name from literal arguments.
- `sqlite3Fts5ConfigSetValue()` applies one runtime config key such as `pgsz`, `hashsize`, `automerge`, `usermerge`, `crisismerge`, `deletemerge`, `rank`, `secure-delete`, or `insttoken`.
- `sqlite3Fts5ConfigLoad()` reads `%_config`, installs defaults, validates file-format version, and records the cookie.
- `sqlite3Fts5ConfigErrmsg()` routes formatted errors to `sqlite3_vtab.zErrmsg` when available.

## Control flow
Declaration parsing tokenizes each CREATE VIRTUAL TABLE argument into either a column definition or an option assignment. `fts5ConfigGobbleWord()` accepts quoted identifiers and barewords. Option assignments go to `fts5ConfigParseSpecial()`, which handles prefix lists, tokenizer argument tokenization, content modes, content-rowid, boolean options, detail mode, locale, and tokendata. Column arguments go to `fts5ConfigParseColumn()`, which rejects reserved `rank` and `rowid` names and records optional `UNINDEXED`.

After scanning arguments, `sqlite3Fts5ConfigParse()` enforces cross-option constraints: `contentless_delete=1` requires contentless tables and is incompatible with `columnsize=0`; `contentless_unindexed=1` requires contentless tables. It then synthesizes the default content table target if no `content=` was specified: normal tables use `%_content`; contentless tables with docsize enabled use `%_docsize`; contentless-unindexed tables may switch to `FTS5_CONTENT_UNINDEXED`. Finally it defaults `content_rowid` to `rowid` and builds `zContentExprlist`, which is the select-list fragment used to retrieve rowid, column values, and optional locale columns.

Runtime loading first resets defaults for page size, merge settings, hash size, and delete merge, then scans `%_config`. All keys other than `version` are applied through `sqlite3Fts5ConfigSetValue()`. File-format version must match `FTS5_CURRENT_VERSION` or `FTS5_CURRENT_VERSION_SECUREDELETE`.

## State and persistence behavior
`Fts5Config` stores both declaration-time state and persistent shadow-table settings. Declaration-time state is in memory but determines which shadow tables and SQL fragments are used. `%_config` values are persistent and are loaded into fields such as `pgsz`, `nAutomerge`, `nUsermerge`, `nCrisisMerge`, `nHashSize`, `zRank`, `zRankArgs`, `bSecureDelete`, `nDeleteMerge`, and `bPrefixInsttoken`. Tokenizer instances are loaded lazily and cached in `pConfig->t`.

## Dependencies and integration points
The file depends on the buffer helpers for SQL assembly, allocation helpers from `fts5_buffer.c`, tokenizer loading from `fts5_main.c`/`fts5_tokenizer.c`, SQLite SQL preparation/stepping/finalization APIs, SQLite value APIs, and constants from `fts5Int.h`. Storage and index modules consume the resulting config for table names, content modes, merge parameters, tokenizer behavior, locale behavior, and file-format validation.

## Risks and edge cases
- Option matching is prefix-based through `sqlite3_strnicmp(name, zCmd, nCmd)`, so ambiguous abbreviations are rejected only in enum parsing, not all option paths.
- Tokenizer directive parsing accepts only space as config whitespace in helper routines, whereas expression parsing accepts tabs/newlines too.
- `fts5ConfigGobbleWord()` allocates a full input-length copy for each word, which is simple but may be wasteful for long malformed inputs.
- Rank parsing only accepts SQL literals in the argument list; expressions are intentionally rejected.
- Cross-option rules are important for contentless tables. Missing tests here can create configurations that later storage/index code cannot satisfy.
- File-format validation reports a rebuild hint. Incorrect version constants or secure-delete transitions can make existing indexes unreadable.

## Test signals
Tests should cover quoted and bare column names, reserved column/table names, malformed quotes, prefix range/limit errors, duplicate tokenizer/content/content_rowid directives, contentless-delete constraints, contentless-unindexed behavior with unindexed columns, locale-enabled expression lists, tokenizer v1/v2 dispatch, rank parsing with literals and malformed expressions, `%_config` defaults and bounds, secure-delete version loading, and invalid config version error messaging.
