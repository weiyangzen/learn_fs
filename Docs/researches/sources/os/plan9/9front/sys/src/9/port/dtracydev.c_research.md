# File Research: sources/os/plan9/9front/sys/src/9/port/dtracydev.c

Provides the DTrace-like `dtracy` provider for Plan 9 `Dev` operations. It registers entry and return probes for walk, stat, open, create, close, read, bread, write, bwrite, remove, and wstat for each device in `devtab`.

`devprovide` snapshots each original `Dev` into `ledger[i].clean`, then creates probes named like `dev:<device>:<op>:entry` and `dev:<device>:<op>:return`. Enabling a probe swaps the selected operation pointer in `devtab[i]` to a wrapper; disabling restores the clean function pointer.

Wrappers package arguments into `DTTrigInfo.arg[]`, trigger the entry probe, call the original implementation, place the return value in `arg[9]` where applicable, and trigger the return probe. This is invasive instrumentation: correctness depends on preserving original function signatures and restoring function pointers exactly.
