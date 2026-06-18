# File Research: sources/os/bsd/netbsd-src/sys/sys/atomic.h

## Scope

Defines NetBSD's legacy atomic operation prototypes, memory barriers, sanitizer-renamed atomic entry points, and kernel atomic load/store helper macros.

## APIs And Behavior

- Declares `atomic_add_*`, `atomic_and_*`, `atomic_or_*`, `atomic_cas_*`, `atomic_swap_*`, `atomic_inc_*`, and `atomic_dec_*` families for 32-bit, 64-bit, int, long, unsigned variants, and pointers.
- Provides `_nv` variants returning the new value and `_ni` compare-and-swap variants.
- Exposes userland-compatible `atomic_cas_16()` and `atomic_cas_8()`.
- Declares memory barriers: `membar_acquire`, `membar_release`, `membar_producer`, `membar_consumer`, `membar_sync`, deprecated `membar_enter/exit`, and optional `membar_datadep_consumer`.
- Under KASAN, KCSAN, or KMSAN, redirects public atomic names to sanitizer wrapper symbols.
- In kernel builds, defines `atomic_load_relaxed/consume/acquire` and `atomic_store_relaxed/release` using volatile accesses plus barriers, with optional KCSAN instrumentation or hash-locked store fallback.

## Dependencies

- Includes `sys/types.h`, optional `stdint.h`, kernel sanitizer options, `sys/cdefs.h`, and `libkern`.
- Assumes machine atomic implementations and memory barrier functions exist elsewhere.

## Risks And Invariants

- Kernel load/store macros assert object size is at most 4 bytes on ILP32 and 8 bytes on LP64, and that pointers are naturally aligned.
- Non-C11 implementation assumes aligned volatile access of supported sizes is atomic.
- Sanitizer macro redirection must stay complete across all atomic families or instrumentation can miss operations.
