# File Research: sources/os/bsd/openbsd-src/sys/sys/witness.h

Defines lock-order debugging support. It maps lock objects to lock classes, defines generic lock-operation flags, and defines assertion flags such as locked, unlocked, shared, exclusive, recursed, and not-recursed.

Kernel prototypes cover witness initialization, lock init/order checking, lock/unlock/upgrade/downgrade tracking, relative ordering, warnings, assertions, spinlock display, no-release/release-ok marking, thread exit, and sysctls. When `WITNESS` is disabled, the public `WITNESS_*` macros compile to no-ops or neutral return values.
