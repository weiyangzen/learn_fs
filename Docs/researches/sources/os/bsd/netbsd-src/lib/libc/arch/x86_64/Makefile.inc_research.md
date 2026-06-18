# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/Makefile.inc

## Summary
Top-level x86_64 libc architecture build fragment.

## Key Details
- Adds `__sigtramp2.S` unless building for `RUMPRUN`.
- Adds current directory to `CPPFLAGS`.

## Notes
The signal trampoline is excluded for rumprun builds.
