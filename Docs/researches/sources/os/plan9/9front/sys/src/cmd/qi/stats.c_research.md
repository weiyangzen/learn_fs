# File Research: sources/os/plan9/9front/sys/src/cmd/qi/stats.c

Execution statistics and profiling support for `qi`.

Key responsibilities:
- `isum` prints per-instruction counts, percentages, instruction class totals, data/instruction cycle estimates, stalls, syscalls, and branch taken rates.
- `segsum` prints memory segment residency/reference summaries.
- `iprofile` aggregates instruction profile counters by text symbol and prints hot functions with source locations.
- `profcmp` sorts profile entries by descending count.

Dependencies and coupling:
- Uses opcode tables from all instruction modules.
- Uses `iprof[]` populated by `mem.c:ifetch`, symbol APIs, and segment state.

Filesystem/OS relevance:
- Reports simulated memory residency for text/data/bss/stack and source-level profiling information.
