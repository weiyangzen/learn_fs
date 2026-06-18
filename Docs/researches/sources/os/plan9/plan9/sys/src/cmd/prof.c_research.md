# File Research: sources/os/plan9/plan9/sys/src/cmd/prof.c

Purpose: Reads Plan 9 profiling data and reports either a call graph or flat time/call table.

Key behavior:
- Options: `-v` verbose sum trace, `-d` graph mode, `-r` allow recursion expansion.
- Loads symbols from an executable using `mach.h` helpers.
- Loads `prof.out`-style binary `Data` records, byte-swapping big-endian fields.
- `graph` recursively prints call tree with recursion suppression unless `-r`.
- `plot` builds symbol accumulators, recursively sums exclusive time, sorts by milliseconds, and prints percentage/time/calls/name.
- `defaout` chooses default executable by `$objtype`.

Dependencies and integration:
- Uses Plan 9 `mach` symbol APIs: `crackhdr`, `syminit`, `textsym`, `findsym`.
- Profiling data format stores `down`, `right`, `pc`, `count`, `time`.

Risks and notes:
- Recursion/cycle handling is only in graph mode; sum assumes tree-like data.
- `time < 0` is checked on unsigned-ish stored data after assignment to long.
- Allocates symbol accumulator incrementally with `realloc`.
