# sources/storage-engines/sqlite/tool/build-shell.sh

## Purpose
`build-shell.sh` demonstrates a full-featured Linux build of the SQLite command-line shell from an amalgamation build directory. It is a developer convenience script rather than a portable production build system.

## Important APIs, Types, and Functions
The script invokes `make sqlite3.c`, then calls `gcc` with SQLite feature defines and source files: `../sqlite/src/shell.c`, `../sqlite/ext/misc/vfstrace.c`, and generated `sqlite3.c`. It links against `dl`, `readline`, and `ncurses`.

## Control Flow
The script assumes it is run from a build directory adjacent to a source checkout named `sqlite`. It first creates or updates `sqlite3.c` through the current Makefile, then compiles `sqlite3` with debug symbols, size optimization, single-thread mode, VFSTRACE, STAT3, FTS4, RTREE, and readline support.

## State and Persistence
It writes the `sqlite3` executable in the current directory and may update generated amalgamation files via `make`. There is no internal state beyond shell process status.

## Dependencies and Integration Points
Dependencies include Bourne shell, make, gcc, a working SQLite build tree layout, readline/ncurses development libraries, and platform linker support for `-ldl`. The script integrates with the SQLite source tree and its generated amalgamation.

## Risks
Paths and libraries are Linux-specific and layout-specific. It does not set `set -e`, so a failed `make sqlite3.c` may still be followed by `gcc`. Feature flags are historical and may not match current recommended builds. STAT3 is obsolete in many modern SQLite configurations.

## Test Signals
A successful run produces an executable `sqlite3` that starts, reports expected compile options through `PRAGMA compile_options`, and can run a basic query. Failure signals include missing sibling source paths, missing readline headers/libraries, and absent Makefile targets.
