# File Research: sources/os/plan9/9front/sys/src/cmd/prof.c

Profiler report reader for Plan 9 profiling output. It reads symbols from an executable via `libmach`, reads a binary `prof.out`-style data file, and prints either a call graph (`-d`) or flat time/call summary.

Key behavior:
- `datas` validates magic `pr\x0f`, reads cycle frequency, and decodes big-endian records into `Data`.
- `graph` recursively prints call tree entries with recursion suppression unless `-r`.
- `plot` builds a text-symbol accumulator table, calls `sum`, sorts by ticks, and prints percentage/time/calls/name.
- `sum` subtracts child time to compute self time.

Integration points:
- Uses `<mach.h>` symbol APIs: `crackhdr`, `syminit`, `textsym`, `findsym`.
- Expects profiling data record layout matching `Datasz = 20`.

Risks:
- Assumes data file endianness/layout exactly.
- Recursive traversal can be deep; malformed indexes are checked but only print diagnostics.
- `static indent;` in `sum` relies on implicit `int`.
