# File Research: sources/os/plan9/plan9/sys/src/cmd/kprof.c

Read fully: 142 lines, 2664 bytes. SHA-256 prefix: `33efe7aa4b8ad1e6`.

This command reads a kernel text binary and profiling data, attributes PC-bucket counts to text symbols, sorts by time, and prints a profile table.

`main()` opens the text file, parses its executable header with `crackhdr()`, initializes symbols with `syminit()`, reads big-endian counter data, prints total/in-kernel/outside counts, compares kernel base against the first text symbol, then walks text symbols accumulating buckets at `PCRES` resolution. Nonzero totals become `COUNTER` entries sorted by `compar()` and printed as milliseconds, percentage, and symbol name.

Dependencies: Plan 9 `mach` library for executable headers and symbols, `bio` for buffered output.

Risk notes: assumes profiling data begins with total and outside-kernel counters, followed by PC buckets. Sorting is ascending and printed backward for descending output.
