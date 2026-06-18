# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_csan.c

## Summary
Implements NetBSD KCSAN runtime support: compiler instrumentation entry points, sampled race detection, reporting, and wrappers for memory, copy, atomic, and bus-space operations.

## Main Responsibilities
- Tracks one sampled memory access cell per CPU.
- Reports overlapping racy accesses with CPU, access type, address, size, PC, and symbol name.
- Provides `__tsan_read*`, `__tsan_write*`, range, init, and function entry/exit hooks.
- Wraps compiler-builtins for `memcpy`, `memcmp`, `memset`, `memmove`, `strcpy`, `strcmp`, and `strlen`.
- Wraps kernel copy routines to annotate kernel-side buffers.
- Generates KCSAN-aware atomic operation wrappers through macros.
- Generates KCSAN-aware bus-space multi/region read/write wrappers.

## Important Behavior
`kcsan_access()` ignores disabled or MD-unsupported addresses, compares the new access with all CPUs' sampled cells, and reports when ranges overlap and at least one non-atomic write participates. Sampling happens every `KCSAN_NACCESSES` accesses per CPU, with interrupts disabled around publishing the cell and a short MD delay.

Atomic wrappers mark accesses as atomic so atomic-vs-atomic conflicts are suppressed. Non-atomic memory and bus-space wrappers annotate the relevant source or destination buffer before invoking the underlying primitive.

## Dependencies
Uses MD hooks from `<machine/csan.h>`, `ksyms_getname()`, `pserialize`, CPU numbering, compiler TSAN ABI names, kernel atomic APIs, copy APIs, and bus-space APIs.

## Risks
Detection is probabilistic and intentionally samples, so absence of reports is not proof of race freedom. Reporting relies on lockless snapshots of other CPU cells and can report approximate PCs/ranges while prioritizing low runtime overhead.
