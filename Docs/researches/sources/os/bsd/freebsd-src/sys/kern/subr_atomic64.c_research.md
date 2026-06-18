# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_atomic64.c

## Summary
Provides software-emulated 64-bit atomic operations for kernel platforms that need them.

## Main Responsibilities
- Implements add, clear, fetchadd, load, set, subtract, store, swap, compare-and-set, and fcompare-and-set for 64-bit values.
- Serializes emulated operations with a hashed mutex pool on SMP kernels.
- Serializes emulated operations by disabling interrupts on non-SMP kernels.
- Initializes the SMP mutex pool at lock subsystem initialization time.

## Key APIs
- `atomic_add_64()`, `atomic_clear_64()`, `atomic_fetchadd_64()`, `atomic_load_64()`, `atomic_set_64()`, `atomic_subtract_64()`, `atomic_store_64()`, `atomic_swap_64()`.
- `atomic_cmpset_64()`, `atomic_fcmpset_64()`.

## Important Behavior
On SMP, the mutex for an address is selected by extracting the physical address with `pmap_kextract()`, dividing by estimated cacheline size, and hashing into a `MAXCPU`-sized mutex pool. Locks are only taken after `smp_started`; before then, startup is effectively single-threaded.

`atomic_fcmpset_64()` follows the FreeBSD convention of updating `*old` with the observed value on failure.

## Dependencies
Uses machine atomic declarations, SMP state, mutexes, interrupt disable/restore, pmap physical address extraction, and SYSINIT for mutex setup.

## Risks
This is atomic only for participants using the same emulation path. Any native or lock-free access to the same 64-bit word can race. The SMP hash serializes by physical cacheline approximation, so correctness depends on stable kernel mappings for the target addresses.
