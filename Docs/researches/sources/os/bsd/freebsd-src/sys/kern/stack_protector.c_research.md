# File Research: sources/os/bsd/freebsd-src/sys/kern/stack_protector.c

## Summary
Provides the kernel stack-protector guard and failure hook used by compiler-inserted stack canary checks.

## Main Responsibilities
- Defines global `__stack_chk_guard[8]`.
- Implements `__stack_chk_fail()` by panicking with a stack-overflow/corruption warning.
- Initializes the guard with random data once kernel randomness is available.

## Important Behavior
`__stack_chk_init()` runs as a `SYSINIT` at `SI_SUB_RANDOM`, fills a temporary guard array using `arc4rand()`, then copies it into the global guard. The fail path panics because a corrupted stack means the backtrace may also be unreliable.

## Dependencies
Uses kernel `SYSINIT`, `arc4rand()`, `panic()`, and `nitems()`.

## Risks
Before random initialization, the guard is zero-filled. The file relies on system initialization order to replace it as early as the random subsystem permits.
