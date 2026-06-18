# File Research: sources/os/plan9/9front/sys/src/cmd/ki/stats.c

Runtime statistics and profiling output for `ki`. `isum` walks all instruction tables, prints per-op counts, aggregates loads/stores/arithmetic/FP/special-register/syscall/branch counts, and reports estimated instruction, data, stall, annulled, and delay-slot cycles.

`segsum` prints resident bytes and reference counts for stack/text/data/bss segments. `iprofile` aggregates instruction-profile counters by text symbol, sorts hot functions by count, prints cycle percentages with source locations, and clears the profile array. This file is diagnostic-only and consumes counters maintained by `run.c` and `mem.c`.
