# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_pcpu.c

## Purpose
Provides machine-independent per-CPU (`pcpu`) and dynamic per-CPU (`dpcpu`) support.

## Main Interfaces
- `pcpu_init()`, `pcpu_destroy()`, `pcpu_find()`: lifecycle and lookup for `struct pcpu`.
- `dpcpu_init()`: initializes per-CPU dynamic storage from linker defaults.
- `dpcpu_alloc()`, `dpcpu_free()`, `dpcpu_copy()`: module-oriented dynamic per-CPU allocator and initializer.
- `sysctl_dpcpu_quad()`, `sysctl_dpcpu_long()`, `sysctl_dpcpu_int()`: aggregate per-CPU counters.
- DDB commands for `dpcpu_off`, `pcpu`, and all pcpu display.

## Implementation Notes
`pcpu_init()` clears the architecture-provided structure, records CPU ID, installs it in `cpuid_to_pcpu`, links it into `cpuhead`, calls machine-dependent initialization, initializes rm queue links, and records zpcpu offset.

`dpcpu_init()` copies static linker-section defaults into a CPU's dynamic area and records its offset in `dpcpu_off`. `dpcpu_startup()` seeds the module dynamic area with `modspace` and initializes an sx lock. Allocation is first-fit with pointer-size rounding. Freeing reinserts a sorted extent and merges adjacent free regions.

General UMA per-CPU zones for 4/8/16/32/64-byte allocations are created during counter startup.

## Dependencies
Uses DPCPU macros, UMA per-CPU zones, SMP CPU iteration, sx locks, malloc type `M_PCPU`, DDB, WITNESS display, and machine pcpu hooks.

## Research Notes
Per-CPU storage is central for scalable counters, scheduler state, lock profiling, PRNG state, and filesystem/VFS hot-path metrics.
