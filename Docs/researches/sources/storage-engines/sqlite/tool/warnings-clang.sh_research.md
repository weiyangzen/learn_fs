# sources/storage-engines/sqlite/tool/warnings-clang.sh

## Purpose
`warnings-clang.sh` runs Clang Static Analyzer (`scan-build`) over selected SQLite amalgamation builds to detect warnings.

## Important APIs, types, and functions
The script removes generated `sqlite3.c` and `shell.c`, rebuilds them with make, then invokes `scan-build gcc -c` for an FTS4/RTREE debug build and a STAT3 threadsafe-off build. It filters out `ANALYZE:` lines.

## Control flow
Execution is linear: clean generated files, make amalgamation and shell, run two analyzer compile commands, print labeled sections.

## State and persistence behavior
It deletes and regenerates `sqlite3.c` and `shell.c`, then creates compiler outputs as side effects. Reports go to stdout/stderr.

## Dependencies and integration points
It depends on shell, make, scan-build, gcc, and SQLite build rules. It is a manual static-analysis helper.

## Risks and edge cases
The shebang is written as `#/bin/sh` rather than `#!/bin/sh`, so direct execution may fail unless invoked through `sh`. No strict error handling is enabled. Analyzer availability and GCC/Clang wrapper behavior are environment-specific.

## Test signals
Successful make generation and analyzer output with no actionable warnings are the primary signals. Direct execution should also verify whether the shebang is tolerated by the caller.
