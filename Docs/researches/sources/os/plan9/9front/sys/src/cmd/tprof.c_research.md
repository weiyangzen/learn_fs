# File Research: sources/os/plan9/9front/sys/src/cmd/tprof.c

Read completely: 147 lines, 2737 bytes.

Time profiler report tool for Plan 9 process profile data. It reads an executable’s symbol table and `/proc/<pid>/profile`, aggregates profile ticks into text symbols, sorts by time, and prints milliseconds/percentage/symbol.

Key behavior:
- With one argument, uses `/proc/<pid>/text`; with two, uses the supplied binary.
- Uses `crackhdr`, `machbytype`, `syminit`, and `textsym` from `<mach.h>`.
- Converts profile words through `machdata->swal`.
- Uses `PCRES` of 8 bytes to map profile buckets to symbol address ranges.

Reliability notes:
- Assumes profile data layout begins with total and secondary count, followed by PC buckets.
- `compar` sorts ascending and output walks backward for descending time.
