# sources/storage-engines/sqlite/tool/libvers.c

## Purpose
`libvers.c` is a tiny diagnostic utility for linking against an SQLite library of unknown provenance and printing its runtime version metadata. It helps confirm which SQLite library a build or environment is actually resolving.

## Important APIs, Types, and Functions
- Declares `extern const char *sqlite3_libversion(void);`.
- Declares `extern const char *sqlite3_sourceid(void);`.
- `main()` prints both values with `printf()` and returns success.

## Control Flow
`main()` ignores its arguments, calls `sqlite3_libversion()` and `sqlite3_sourceid()`, prints one line for the version and one line for the source ID, then exits with `0`.

## State and Persistence Behavior
The program has no persistent state, no heap state, no files, and no database handles. Its output is entirely derived from the linked SQLite library.

## Dependencies and Integration Points
- Depends on `stdio.h` and external SQLite symbols supplied by the linked library.
- It intentionally does not include `sqlite3.h`; the two declarations are enough for this probe.
- Useful in build/test environments where `LD_LIBRARY_PATH`, static linking, package manager libraries, or local build artifacts may select different SQLite binaries.

## Risks and Edge Cases
- Link-time failure indicates the selected library does not export the expected symbols.
- Runtime dynamic loader selection can still differ from compile-time expectations; the output is useful precisely because it reports the loaded library.
- The unused `argc`/`argv` may trigger warnings under strict warning policies.

## Test Signals
- Compile and link against a known SQLite build, run the binary, and compare printed version/source ID to the expected build.
- Repeat with dynamic library path changes to confirm it reports the runtime-loaded library.
