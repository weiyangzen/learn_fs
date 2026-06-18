# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_early.c

## Purpose
Provides early-boot wrappers for memory routines before the normal runtime environment is fully available.

## Key Elements
- `memset_early()`.
- `memcpy_early()`.
- `memmove_early()`.
- Optional machine-specific overrides: `MEMSET_EARLY_FUNC`, `MEMCPY_EARLY_FUNC`, `MEMMOVE_EARLY_FUNC`.

## Behavior
Each wrapper calls either the normal libc/kernel routine or a machine-provided early implementation selected by preprocessor macro. If no machine override exists, the wrapper maps directly to `memset`, `memcpy`, or `memmove`.

## Research Notes
The file is intentionally small and exists to provide stable MI names for early boot code while letting architectures swap in safe implementations for periods when normal code may not be usable.
