# sources/storage-engines/sqlite/tool/symbols.sh

## Purpose
`symbols.sh` is the Unix-oriented symbol audit script for SQLite amalgamation builds. It verifies exported public symbols and undefined dependencies under feature-rich and core configurations.

## Important APIs, types, and functions
The script runs `make sqlite3.c`, compiles with GCC and feature defines including FTS3, RTREE, STAT3, MEMSYS5, unlock notify, column metadata, preupdate hook, session, FTS5, and GEOPOLY, then uses `nm`, `grep`, `egrep`, and `sort`.

## Control flow
It prints four reports: exported symbols from the extension-rich object, surplus exported symbols excluding accepted `sqlite3`, session, rebaser, changeset, and changegroup prefixes, undefined dependencies for a no-OS/no-thread core build, and undefined dependencies for an RTREE/FTS4 build.

## State and persistence behavior
The script regenerates `sqlite3.c` and repeatedly overwrites `sqlite3.o` in the working directory. Output is stdout-only.

## Dependencies and integration points
It depends on make, GCC, nm, grep/egrep/sort, and SQLite amalgamation build rules. It is a release engineering and ABI hygiene helper.

## Risks and edge cases
No strict error mode is set. Regex allowlists encode policy and may need updates when new public APIs are added. Results depend on compiler, platform object format, and `nm` formatting.

## Test signals
A clean run should show only intentional public exports, no unexpected surplus symbols, and dependency lists consistent with the selected core/extension builds.
