# sources/storage-engines/sqlite/tool/warnings.sh

## Purpose
`warnings.sh` compiles SQLite amalgamation variants with strict GCC warning flags to check for compiler warnings across feature configurations.

## Important APIs, types, and functions
The script determines warning flags by platform and GCC version. It builds `sqlite3.c`, then compiles feature-rich, Android-like Linux, STAT4 threadsafe-off, and optimized FTS/GEOPOLY configurations.

## Control flow
It sets `WARNING_OPTS` and `WARNING_ANDROID_OPTS`, removes `sqlite3.c`, runs `make sqlite3.c`, prints labeled sections, and invokes `gcc -c` with selected macro sets. On Linux it also compiles `sqlite3.c shell.c` with Android-oriented defines and ICU/load-extension omissions.

## State and persistence behavior
It regenerates `sqlite3.c` and produces object files in the current directory. It emits diagnostics to stdout/stderr but does not write reports.

## Dependencies and integration points
It depends on shell, uname, GCC, make, and SQLite generated sources. It is a local warning-gate helper used by maintainers.

## Risks and edge cases
The shebang is `#/bin/sh`, so direct execution may not select a shell. GCC version comparison is lexical and can be fragile. The `SQLITE_ENABLE_MATH_FUNCTIONS_fixme` define looks intentionally nonstandard and may be used to test warning behavior rather than enable the feature. No `set -e` means failures may cascade.

## Test signals
Expected test signals are warning-free compiler output in all labeled sections, correct OpenBSD/Linux/macOS flag selection, and Android configuration compilation on Linux.
