# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/prep/edit.h

This header defines the shared partition editor data model.

Key structures:
- `Part`: partition name, ctl name, start/end, ctl start/end overrides, and changed flag.
- `Edit`: disk pointer, current ctl partitions, desired partitions, callbacks, unit name, auxiliary pointer, dot/end values, and internal changed/warning/last-command state.

Key declarations:
- Generic editor functions: `getline`, `runcmd`, `findpart`, `addpart`, `delpart`.
- Expression parser: `parseexpr`.
- Kernel ctl reconciliation: `ctldiff`.
- Allocation helpers: `emalloc`, `estrdup`.

Role:
- Shared ABI for `edit.c`, `fdisk.c`, `prep.c`, and `calc.y`.
