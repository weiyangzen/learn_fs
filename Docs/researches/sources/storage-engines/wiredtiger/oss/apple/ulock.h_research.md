# sources/storage-engines/wiredtiger/oss/apple/ulock.h

This header provides Apple `ulock` declarations, operation codes, flags, and masks. Under `PRIVATE`, it declares `__ulock_wait`, `__ulock_wait2`, and `__ulock_wake` for non-kernel code, defines compare-and-wait and unfair-lock operation IDs, wake/wait/generic flags, and masks for operation construction. `ulock_owner_value_to_port_name` maps owner values to Mach port names differently for kernel-private and non-kernel builds.

The header owns no runtime state; it defines ABI-level constants. It depends on Mach port types, `sys/cdefs.h`, and fixed-width integer types. Risks are private Apple interface drift, macro-gated availability, and incorrect operation/flag combinations. Compile coverage on Darwin and runtime tests in synchronization code are the main signals.
