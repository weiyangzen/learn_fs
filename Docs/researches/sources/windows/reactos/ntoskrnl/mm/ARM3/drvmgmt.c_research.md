# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/drvmgmt.c

Read status: complete file, 254 lines.

This file contains ARM3 driver-management and driver-verifier support routines, with pageable-image locking/trimming mostly stubbed and verifier thunk registration partially implemented.

Key entry points:
- `MmUnlockPageableImageSection()`, `MmLockPageableSectionByHandle()`, `MmLockPageableDataSection()`, and `MmTrimAllSystemPageableMemory()` are unimplemented or warning stubs.
- `MmAddVerifierThunks()` validates a driver-supplied thunk-pair table, allocates a private copy, locates the owning loader entry, rejects kernel/HAL thunks, verifies pristine routines are inside the owning image, and links the thunk table into `MiVerifierDriverAddedThunkListHead`.
- `MmIsDriverVerifying()` checks the driver's loader entry for `LDRP_IMAGE_VERIFYING`.
- `MmIsVerifierEnabled()` reports `MmVerifierData.Level` when verifier thunk infrastructure has been initialized, otherwise returns `STATUS_NOT_SUPPORTED`.

Important dependencies:
- Verifier globals: `MmVerifierData`, `MiVerifierDriverAddedThunkListHead`, `MiActiveVerifierThunks`.
- Loader state: `MiLookupDataTableEntry()`, `PLDR_DATA_TABLE_ENTRY`, `MmSystemLoadLock`, `MmBootImageSize`.
- Driver object loader section (`DriverObject->DriverSection`).

Notable behavior and risks:
- `MmAddVerifierThunks()` checks each thunk's `PristineRoutine`, but the loop uses `ThunkTable->PristineRoutine` instead of `ThunkTable[i].PristineRoutine`, so only the first entry is effectively validated repeatedly.
- Verifier availability is inferred from `MiVerifierDriverAddedThunkListHead.Flink` being initialized/non-null.
- Pageable image section lock/unlock behavior is not implemented, so callers get no real memory residency management here.
