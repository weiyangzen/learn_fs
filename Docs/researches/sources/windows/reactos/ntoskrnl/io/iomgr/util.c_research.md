# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/util.c

## Role

`util.c` contains miscellaneous I/O-manager helper APIs for cancel-lock acquisition, stack limit discovery, process/thread queries, WDM version checks, access validation, EA buffer validation, and verify-device bookkeeping.

## Main entry points and behavior

- `IoComputeDesiredAccessFileObject()` verifies the object type is `IoFileObjectType` and computes write/append desired access, omitting `FILE_APPEND_DATA` for named pipes to avoid conflict with pipe-instance creation (lines 24-47).
- `IoAcquireCancelSpinLock()` and `IoReleaseCancelSpinLock()` wrap queued spin lock operations on `LockQueueIoCancelLock` (lines 51-60, 145-154).
- `IoGetInitialStack()` returns the current thread TCB initial stack (lines 62-71).
- `IoGetStackLimits()` reads normal stack limits through `RtlpGetStackLimits()` and substitutes DPC stack limits if the current stack address is outside the normal range while running an active DPC at dispatch level or higher (lines 73-108).
- `IoIsSystemThread()`, `IoGetCurrentProcess()`, and `IoThreadToProcess()` are thin wrappers around thread/process fields or process-manager helpers (lines 110-119, 134-143, 156-165).
- `IoIsWdmVersionAvailable()` reports support up to WDM 1.30 (Windows Server 2003) using simple major/minor comparison (lines 121-132).
- `IoCheckDesiredAccess()` maps generic file-object access and checks requested access against granted access (lines 167-184).
- `IoCheckEaBufferValidity()` walks a `FILE_FULL_EA_INFORMATION` chain, validating base size, name/value bounds, null-terminated names, aligned next offsets, positive offsets, and remaining length. On failure it returns `STATUS_EA_LIST_INCONSISTENT` and reports the failing offset (lines 186-269).
- `IoSetDeviceToVerify()`, `IoSetHardErrorOrVerifyDevice()`, and `IoGetDeviceToVerify()` store or retrieve the thread's device-to-verify pointer; the IRP form ignores IRPs with no associated thread (lines 299-340).

## Implementation gaps and risks

- `IoCheckFunctionAccess()`, `IoValidateDeviceIoControlAccess()`, and `IoCheckQuerySetVolumeInformation()` are unimplemented and return `STATUS_NOT_IMPLEMENTED` (lines 271-297, 342-353).
- `IoCheckDesiredAccess()` uses `(~(*DesiredAccess) & GrantedAccess)` to decide denial (lines 181-183). That expression is unusual for testing whether all desired bits are granted; readers should verify it against the intended Windows semantics before relying on it.
- `IoIsWdmVersionAvailable()` does not compare major/minor as a lexicographic version; it returns true only when `MajorVersion <= 1 && MinorVersion <= 0x30`, which is fine for the current advertised support but not a general version predicate (lines 124-131).
