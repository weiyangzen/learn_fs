# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/locale/compat_setlocale32.c

## Scope

HPPA 32-bit compatibility wrapper for `setlocale`.

## Behavior

- Provides compatibility glue for older HPPA locale ABI.
- Delegates locale selection to the modern libc locale implementation while preserving the old exported symbol/ABI surface.

## Dependencies And Invariants

- Exists because HPPA compatibility needs architecture-specific locale handling in addition to syscall wrappers.
- Correctness depends on matching old pointer/return ABI expectations.
