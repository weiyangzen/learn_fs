# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/CrNtStubs.h

## Purpose

`CrNtStubs.h` is the CrossNt symbol table. It lists NT/HAL/NDIS routines that the portability layer can dynamically bind or emulate.

## Main Contents

Macro invocations declare entries for:

- Process/thread identity:
  - `PsGetCurrentProcessId`
  - `PsGetCurrentThreadId`
- Spin/interlocked operations:
  - `KeTestSpinLock`
  - `InterlockedIncrement`
  - `InterlockedDecrement`
  - `InterlockedExchangeAdd`
  - `InterlockedCompareExchange`
- HAL IRQL helpers:
  - `KeRaiseIrqlToDpcLevel`
  - `KeRaiseIrqlToSynchLevel`
- NDIS read/write locks:
  - `NdisInitializeReadWriteLock`
  - `NdisAcquireReadWriteLock`
  - `NdisReleaseReadWriteLock`

## Integration Notes

This file depends entirely on `CROSSNT_DECL` and `CROSSNT_DECL_EX` being defined before inclusion, normally by `CrNtDecl.h`. It enables the same list to produce typedefs, globals, and initialization code.

## Risks And Edge Cases

- The listed prototypes must exactly match the real exported routines and calling conventions.
- Some call-argument macro payloads include parameter declarations rather than plain arguments in interlocked entries, which is harmless only if the active macro ignores or tolerates that field.
- NDIS lock support depends on `NDIS.SYS` availability; fallback behavior depends on implementations elsewhere.
