# File Research: sources/os/bsd/freebsd-src/sys/sys/atomic_common.h

Common atomic load/store helper macros for machine atomic headers.

Key elements:
- Refuses direct inclusion unless `_MACHINE_ATOMIC_H_` is defined.
- Defines relaxed volatile load/store helpers for bool, char, short, int, long, and fixed-width 8/16/32/64-bit types.
- Uses C11 `_Generic` when available for type checking.
- Defines public `atomic_load_*`, `atomic_store_*`, pointer load/store, consume pointer load, and interrupt fence helpers.

Dependencies:
- Includes `sys/types.h`.
- Depends on architecture-provided acquire pointer load and compiler memory barrier macros.

Research notes:
- Shared implementation layer behind architecture atomic APIs.
- 64-bit scalar helpers are exposed only on LP64.
