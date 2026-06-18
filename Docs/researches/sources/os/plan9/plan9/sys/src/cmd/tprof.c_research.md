# File Research: sources/os/plan9/plan9/sys/src/cmd/tprof.c

Per-function profiler report tool for Plan 9 process profile data.

Key responsibilities:
- Accepts `pid` and optional binary path.
- Reads symbols from `/proc/<pid>/text` or the supplied binary using libmach.
- Reads raw profiling counters from `/proc/<pid>/profile`.
- Swaps counter endianness using selected machine data.
- Maps PC bucket counts to text symbols using page-aligned text base and `PCRES`.
- Accumulates time per function, sorts by count, and prints milliseconds, percentage, and symbol.

Important behavior:
- `data[0]` and `data[1]` are used to compute total and delta.
- If total count is zero, exits without a report.
- Requires text symbols; errors if none are found.

Notable risks:
- Percentage uses `delta = data[0] - data[1]`, so malformed profile data can distort output.
- Function ranges are inferred from symbol order and PC bucket offsets.
