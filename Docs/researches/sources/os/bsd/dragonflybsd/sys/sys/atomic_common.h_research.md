# File Research: sources/os/bsd/dragonflybsd/sys/sys/atomic_common.h

Read completely: 131 lines.

This header provides common relaxed atomic load/store macros for machine atomic headers.

Key contents:
- Rejects direct inclusion unless `_CPU_ATOMIC_H_` is defined.
- Defines volatile relaxed loads and stores for bool, char, short, int, long, and fixed-width 8/16/32/64-bit types.
- Uses C11 `_Generic` or compiler generic-selection support to provide type checking where available.
- Defines public `atomic_load_*` and `atomic_store_*` macros, with 64-bit generic operations only under `__LP64__`.
- Defines pointer load/store helpers using volatile `typeof`.

Security/reliability notes:
- These are relaxed operations only; they do not imply memory ordering barriers.
- Macro arguments are evaluated in volatile contexts and should be real object pointers of the expected type.
