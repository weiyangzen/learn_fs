# File Research: sources/os/bsd/freebsd-src/sys/sys/reg.h

Read completely: 91 lines.

## Purpose
Wraps machine register definitions and declares kernel register-set infrastructure for ptrace/core/debug consumers.

## Main Elements
- Includes `<machine/reg.h>`.
- Under `_KERNEL`, defines `regset_get` and `regset_set` callback types.
- Defines `struct regset` with ELF note id, size, get callback, and set callback.
- Declares linker sets for native and compat32 ELF register sets.
- Declares native register/fpreg/dbreg fill and set functions.
- Declares compat32 register accessors when `COMPAT_FREEBSD32` is enabled, with macro-guarded declarations for optional machine overrides.

## Dependencies And Integration
Integrated with ELF core note generation, ptrace register access, machine-dependent register layouts, linker sets, and compat32 support.

## Risk Notes
Register-set note IDs, sizes, and callbacks are consumed by debuggers and core dump code. Machine headers control actual layout, so compatibility must be preserved per architecture.
