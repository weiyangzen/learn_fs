# sources/storage-engines/sqlite/ext/icu/icu.c

## Purpose
`icu.c` integrates ICU with SQLite. It registers ICU-backed SQL functions for `regexp`, `upper`, `lower`, `like`, and `icu_load_collation`, depending on build macros, and exposes the loadable extension entry point.

## Important APIs, Types, And Functions
The initializer is `sqlite3IcuInit(sqlite3 *db)`. Loadable builds export `sqlite3_icu_init()`. SQL functions are implemented by `icuRegexpFunc()`, `icuCaseFunc16()`, `icuLikeFunc()`, and `icuLoadCollation()`. Support functions include `icuLikeCompare()`, `icuRegexpDelete()`, `icuCollationColl()`, `icuCollationDel()`, and `icuFunctionError()`. ICU calls include regex, string case mapping, fold-case, and collation APIs.

## Control Flow
`sqlite3IcuInit()` registers enabled functions from a static table. `icuLikeFunc()` validates optional ESCAPE, checks pattern length, and calls recursive Unicode-folding LIKE comparison. `icuRegexpFunc()` caches compiled ICU regexes in SQLite auxdata, sets input text, runs a full match, clears text, and returns a boolean. `icuCaseFunc16()` converts UTF-16 text to upper/lower with optional locale and retries on buffer overflow. `icuLoadCollation()` opens an ICU collator, optionally sets strength, and registers a UTF-16 SQLite collation with a destructor.

## State And Persistence
Functions and collations are per-connection. Regex auxdata lives for a statement execution. Collators live until collation destruction. Database files are not modified, but schemas can persist collation names that require the extension later.

## Dependencies And Integration Points
The module depends on ICU headers/libraries and SQLite extension/core APIs. `sqliteicu.h` exposes static initialization. Function flags include deterministic/innocuous for scalar functions and direct-only for collation loading.

## Risks
LIKE recursion requires the pattern length guard. ICU version changes can alter results. Collation names become load-order dependencies. Locale-specific case mapping can differ from SQLite ASCII behavior. Weakening `SQLITE_DIRECTONLY` on collation loading would affect security posture.

## Test Signals
Cover Unicode LIKE, ESCAPE validation, pattern length errors, NULL handling, regex invalid/cached patterns, locale-specific case mapping, collation strength validation, extension loading, and build macro variants.
