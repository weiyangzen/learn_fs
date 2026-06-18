# File Research: sources/os/plan9/9front/sys/src/cmd/5i/stats.c

This file reports execution, memory, TLB, and symbol-level profiling statistics for the `5i` ARM interpreter.

Key elements:
- `isum()` walks `itab[]`, totals executed instruction counts, prints per-instruction percentages, and aggregates memory, arithmetic, branch, and syscall categories.
- `tlbsum()` reports TLB hit/miss counts if the interpreter TLB model is enabled.
- `segsum()` prints base/end/resident/reference counts for stack, text, data, and BSS segments.
- `iprofile()` builds function-level profile data from `iprof[]` buckets, maps buckets to text symbols, sorts by count, and prints cycle percentages plus source locations.
- `profcmp()` sorts profile rows descending by count.

Dependencies and integration:
- Uses `Inst itab[]` from `run.c`.
- Uses interpreter globals such as `memory`, `tlb`, `nopcount`, `iprof`, and `textbase`.
- Uses libmach symbol helpers `textsym()` and local `printsource()`.

Notable behavior:
- The instruction-cycle summary treats memory instructions as adding data cycles, printing total “memory cycles” as `mems + total`.
- Branch delay-slot reporting is retained even though ARM itself does not have the same delay-slot semantics as MIPS; it reflects the shared historical simulator reporting style.
- `Prof prof[5000]` is fixed-size and assumes the text symbol count fits.

Research notes:
- This file is reporting-only and does not alter execution except clearing the used profile rows after `iprofile()`.
