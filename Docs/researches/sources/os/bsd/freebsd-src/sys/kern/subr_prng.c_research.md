# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_prng.c

## Purpose
Provides fast per-CPU pseudo-random number generation using PCG. This is not cryptographic randomness; it is a lightweight kernel PRNG utility.

## Main Interfaces
- `prng32()`, `prng32_bounded()`.
- `prng64()`, `prng64_bounded()`.

## Implementation Notes
The file defines per-CPU PCG state for 32-bit and 64-bit random generation. On platforms without 128-bit PCG operations, a local `pcg64u_random_t` gangs two 32-bit PCG states into one 64-bit generator. Bounded 64-bit generation uses rejection sampling with `threshold = -bound % bound`.

`prng_init()` seeds every CPU's 32-bit and 64-bit state with seed value `1` during `SI_SUB_CPU`. Each public function enters a critical section, uses the current CPU's DPCPU state, and exits the critical section so execution cannot migrate midway through state update.

## Dependencies
Uses PCG routines from `sys/prng.h`, DPCPU storage, `CPU_FOREACH`, critical sections, SMP/pcpu APIs, and SYSINIT.

## Research Notes
This is deterministic fast PRNG infrastructure for non-security uses such as randomized backoff or sampling. Filesystem code may use it for low-stakes randomized behavior, but not for entropy.
