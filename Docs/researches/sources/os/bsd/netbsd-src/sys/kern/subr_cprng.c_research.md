# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_cprng.c

## Summary
Implements NetBSD's per-CPU strong CPRNG instances backed by NIST Hash_DRBG and reseeded from the kernel entropy subsystem.

## Main Responsibilities
- Initializes `kern_cprng` and `user_cprng` with different maximum IPLs.
- Creates `kern.urandom` and `kern.arandom` sysctl nodes.
- Allocates per-CPU DRBG and reseed event counter state.
- Reseeds per-CPU DRBGs when the entropy epoch changes or generation requires reseed.
- Provides `cprng_strong()`, `cprng_strong32()`, and `cprng_strong64()`.

## Important Behavior
Per-CPU DRBG state is allocated separately from the `percpu` object because percpu storage may move without zeroing. `cprng_strong()` raises to the instance IPL and holds a percpu reference while generating, but drops both around `entropy_extract()` because entropy extraction may sleep.

`kern.arandom` clamps sysctl reads to 256 bytes and clears the temporary buffer after copying. `kern.urandom` similarly clears the stack integer after sysctl lookup.

## Dependencies
Uses `crypto/nist_hash_drbg`, `percpu`, `entropy_epoch()`/`entropy_extract()`, `evcnt`, sysctl, IPL control, and explicit memory clearing.

## Risks
Callers must obey the context constraints: not hard interrupt context, request length no more than `CPRNG_MAX_LEN`, and legacy `flags == 0`. Reseeding may race benignly across CPUs, intentionally trading extra reseeds for simpler synchronization.
