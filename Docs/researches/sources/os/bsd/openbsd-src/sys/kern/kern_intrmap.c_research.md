# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_intrmap.c

## Purpose
Provides a generic interrupt-to-CPU mapping helper for devices with multiple interrupt vectors/rings.

## Main Responsibilities
- Builds a reference-counted snapshot of CPUs usable for interrupts.
- Excludes secondary SMT threads when `__HAVE_CPU_TOPOLOGY` is available.
- Chooses an interrupt count bounded by requested count, maximum count, and usable CPU count.
- Optionally rounds interrupt count down to a power of two.
- Builds a per-device CPU map offset by device unit to spread interrupts across devices.
- Exposes mapping count and ring-to-CPU lookup.

## Key Entry Points
- `intrmap_create()`: creates an interrupt map for a device.
- `intrmap_destroy()`: frees map and drops CPU snapshot reference.
- `intrmap_count()`: returns number of interrupts/rings.
- `intrmap_cpu()`: returns the CPU assigned to a ring.

## Key Data
- `struct intrmap_cpus`: refcounted usable CPU array.
- `struct intrmap`: interrupt count, grid size, CPU snapshot, per-ring CPU indices.
- Global `intrmap_cpus`, `intrmap_ncpu`, and `intrmap_lock`.

## Notable Algorithm
`intrmap_create()` picks a grid divisor of usable CPU count and offsets by `dv_unit`, so devices with the same number of rings are distributed rather than all starting on CPU zero.

## Dependencies
Uses device unit numbers, global CPU enumeration, malloc/free, refcounts, and rwlock protection.

## Research Notes
This is device-agnostic infrastructure adapted from network ring mapping ideas.
