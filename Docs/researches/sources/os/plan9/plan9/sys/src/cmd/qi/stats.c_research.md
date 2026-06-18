# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/stats.c

Execution statistics and profiling reports for `qi`.

Key responsibilities:
- Aggregates instruction counts across all opcode tables.
- Reports per-instruction counts and percentages.
- Summarizes loads, stores, arithmetic, floating point, special-register operations, control instructions, syscalls, branches, and taken branches.
- Prints simple memory segment residency/reference summaries.
- Builds a symbol-level instruction profile by summing per-PC profile buckets between text symbols.

Dependencies:
- Uses opcode table globals, segment state, profiler arrays, libmach text symbols, and source-line printing.

Notable risks:
- Percent calculation assumes nonzero denominators in some subcategories; branch taken percentage can divide by branch count.
- Instruction-cycle and data-cycle model is approximate and not a full PowerPC timing model.
- Fixed `prof[5000]` limits the number of profiled symbols.
