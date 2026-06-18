# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_csan.c

## Purpose
Implements the FreeBSD kernel concurrency sanitizer runtime. It receives compiler-emitted ThreadSanitizer-style hooks, samples kernel memory accesses, detects overlapping racy accesses across CPUs, and reports them through `printf` or `panic` depending on configuration.

## Key Elements
- Per-CPU state: `kcsan_cpus[MAXCPU]`, `csan_cpu_t`, `csan_cell_t`.
- Runtime enablement: `kcsan_enable()` at `SI_SUB_SMP`.
- Main detector: `kcsan_access(addr, size, write, atomic, pc)`.
- Reporting: `kcsan_report()` with optional DDB symbol lookup and MD unwind.
- Compiler hooks: `__tsan_read*`, `__tsan_write*`, range hooks, init/function-entry no-ops.
- Instrumented libc-style helpers: `kcsan_memcpy`, `kcsan_memcmp`, `kcsan_memset`, `kcsan_memmove`, string helpers, and copyin/copyout wrappers.
- Atomic wrappers from `<sys/atomic_san.h>`.
- Bus-space wrappers from `<sys/bus_san.h>`.

## Behavior
`kcsan_access()` first exits if KCSAN is disabled, the machine-dependent layer rejects the address, or the kernel is panicked. It compares the new access with each CPU's sampled access cell, ignores non-overlaps, read/read pairs, and accesses where all writes are marked atomic, then reports the first conflict.

Sampling is deliberately sparse: every `KCSAN_NACCESSES` accesses, the current CPU publishes one access cell, delays for `KCSAN_DELAY`, then clears it. Interrupt state is managed by the MD layer while publishing the sample.

## Research Notes
This file is runtime glue for compiler and kernel wrappers. The race model is simple and sampling-based: it catches conflicting overlapping accesses only while another CPU has an active sampled cell. Atomic wrappers still record accesses, but conflicts between properly atomic writers/readers are suppressed.
