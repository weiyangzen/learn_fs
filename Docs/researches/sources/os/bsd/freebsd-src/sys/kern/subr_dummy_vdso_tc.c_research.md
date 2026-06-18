# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_dummy_vdso_tc.c

## Purpose
Supplies dummy VDSO timecounter fill routines for platforms that do not provide CPU-specific VDSO timehands support.

## Key Elements
- `cpu_fill_vdso_timehands(struct vdso_timehands *, struct timecounter *)`.
- 32-bit compatibility variant under `COMPAT_FREEBSD32`: `cpu_fill_vdso_timehands32()`.

## Behavior
Both routines return `0` and do not populate their output structures. This indicates that no CPU-specific VDSO timecounter data is available from this implementation.

## Research Notes
This is a compatibility stub. Real architectures that support fast userspace timecounter reads replace these functions with machine-dependent implementations.
