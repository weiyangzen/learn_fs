# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/ilock.h

## Purpose

`ilock.h` declares internal CrossNt fallback implementations for interlocked operations on i386/x86 systems.

## Main Contents

- Declares MP and UP variants for:
  - `CrNtInterlockedIncrement_impl_i386_*`
  - `CrNtInterlockedDecrement_impl_i386_*`
  - `CrNtInterlockedExchangeAdd_impl_i386_*`
  - `CrNtInterlockedCompareExchange_impl_i386_*`

## Integration Notes

This file is included only when `CROSS_NT_INTERNAL` is defined. It supplies prototypes for fallback routines used when the corresponding NT exports are missing or unsuitable.

## Risks And Edge Cases

- The declarations are x86-specific and use `__fastcall`.
- The include guard terminator is written as `#endif __CROSS_NT_INTERLOCKED__H__`, which is nonstandard but accepted by many preprocessors as trailing tokens after `#endif`.
- Correct UP/MP selection must be handled elsewhere based on CPU/system state.
