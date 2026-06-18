# sources/storage-engines/sqlite/ext/fts5/fts5_test_mi.c

## Purpose

`fts5_test_mi.c` is a test-only FTS5 auxiliary function that emulates the older FTS3/FTS4 `matchinfo()` function on top of the FTS5 extension API. It is used to validate FTS5 auxiliary APIs and to provide compatibility-style test data, not as release production code.

## Important APIs, types, and functions

`Fts5MatchinfoCtx` stores table column count, phrase count, the requested flag string, output integer count, and the output `u32` array. `fts5_api_from_db()` retrieves `fts5_api` through `SELECT fts5(?1)`. `fts5MatchinfoFlagsize()` maps each supported flag (`p`, `c`, `x`, `y`, `b`, `n`, `a`, `l`, `s`) to the number of 32-bit integers emitted. `fts5MatchinfoIter()` walks the flag string and invokes either global or local filler callbacks.

`fts5MatchinfoGlobalCb()` fills query/table-wide values such as phrase count, column count, per-phrase global hit/doc counts through `xQueryPhrase`, row count, and average column lengths. `fts5MatchinfoLocalCb()` fills current-row values such as phrase-column bitmaps, local hit counts, column lengths, and longest phrase-sequence lengths. `fts5MatchinfoFunc()` is the registered auxiliary callback. `sqlite3Fts5TestRegisterMatchinfoAPI()` and `sqlite3Fts5TestRegisterMatchinfo()` register the function via `fts5_api.xCreateFunction`.

## Control flow

On first invocation for a cursor, `fts5MatchinfoFunc()` reads the optional flag string (default `pcx`), retrieves cached auxdata, and if needed allocates a new `Fts5MatchinfoCtx` with enough space for all output integers and a copy of the flag string. Context creation computes global fields once using the extension API. Each row invocation then recomputes local fields, returns the `u32` array as a blob, and caches the context as FTS5 auxdata so subsequent rows for the same cursor and flag string reuse global work.

## State and persistence behavior

There is no persistent database state. State is per-cursor auxiliary data owned by FTS5 and destroyed with `sqlite3_free`. The global part of the matchinfo output is cached in the same allocation as local output storage; local fields are overwritten for each row.

## Dependencies and integration points

The file depends only on `fts5.h`, SQLite APIs, and the FTS5 extension API version 2 or newer. It exercises `xColumnCount`, `xPhraseCount`, `xQueryPhrase`, `xPhraseFirst`, `xPhraseNext`, `xRowCount`, `xColumnTotalSize`, `xPhraseFirstColumn`, `xPhraseNextColumn`, `xColumnSize`, `xInstCount`, `xInst`, and `xPhraseSize`.

## Risks and edge cases

The implementation documents behavioral differences from FTS4: FTS5 uses matchable phrases from the matching expression subtree, and global `x` counts ignore NEAR constraints while current-row counts observe them. Output sizes can grow with `nCol * nPhrase`, so allocation size and flag validation are important. The `s` flag's longest-sequence logic assumes ordered instance data from `xInst`. If the table has no rows, average-length output is zeroed to avoid divide-by-zero.

## Test signals

This module is a direct test signal for extension API correctness. Failures in phrase iteration, column-size accounting, row counts, auxdata caching, or instance ordering show up as mismatched `matchinfo()` blobs in Tcl tests. It can be registered through the Tcl command in `fts5_tcl.c` or compiled in via `SQLITE_FTS5_ENABLE_TEST_MI`.
