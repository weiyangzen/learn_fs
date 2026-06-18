# sources/storage-engines/sqlite/tool/version-info.c

## Purpose
`version-info.c` emits SQLite library version metadata, especially JSON consumed by the sqlite3 JavaScript API build.

## Important APIs, types, and functions
It includes `sqlite3.h` unless `TEST_VERSION` is set, then uses `SQLITE_VERSION`, `SQLITE_VERSION_NUMBER`, `SQLITE_SOURCE_ID`, and SCM macros (`SQLITE_SCM_BRANCH`, `SQLITE_SCM_TAGS`, `SQLITE_SCM_DATETIME`). `usage()` documents flags. `main()` parses `--version`, `--version-number`, `--download-version`, `--source-id`, `--json`, and `--quote`.

## Control flow
With no information flags, it defaults to JSON. It computes the download-page integer form from `SQLITE_VERSION_NUMBER`, then either emits a compact JSON object with version/source/SCM fields or one selected scalar, optionally quoted.

## State and persistence behavior
No persistence. Output is stdout only.

## Dependencies and integration points
It depends on SQLite compile-time version macros and standard C. It is integrated into JS/release build steps that need machine-readable version information.

## Risks and edge cases
The JSON path assumes `SQLITE_SOURCE_ID+20` points at the SHA3 portion, which depends on SQLite source ID format. Multiple scalar flags are counted but the output uses the first matching branch in fixed order. Unknown flags print usage and fail.

## Test signals
Run with no flags, each scalar flag, `--quote`, `--json`, and `TEST_VERSION` compilation. Validate JSON fields and download-version arithmetic.
