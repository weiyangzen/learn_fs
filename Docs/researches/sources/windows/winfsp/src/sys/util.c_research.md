# File Research: sources/windows/winfsp/src/sys/util.c

## Purpose

`util.c` is a collection of kernel utility wrappers and support mechanisms used throughout the WinFsp driver. It covers version detection, synchronous internal IRPs, user-buffer handling, cache-manager wrappers, security and EA validation, notification and oplock wrappers, work-item helpers, safe MDLs, IRP completion hooks, and optimized Unicode comparison.

## Main Contents

Major groups:

- Must-succeed allocation helpers:
  - `FspAllocatePoolMustSucceed`
  - `FspAllocateIrpMustSucceed`
- System/version/object utilities:
  - `FspIsNtDdiVersionAvailable`
  - `FspCreateGuid`
  - `FspGetDeviceObjectPointer`
  - `FspRegistryGetValue`
- Synchronous IRP senders:
  - `FspSendSetInformationIrp`
  - `FspSendQuerySecurityIrp`
  - `FspSendQueryEaIrp`
  - `FspSendMountmgrDeviceControlIrp`
  - `FspSendIrpCompletion`
- Buffer and MDL helpers:
  - `FspBufferUserBuffer`
  - `FspLockUserBuffer`
  - `FspMapLockedPagesInUserMode`
  - `FspSafeMdlCheck`
  - `FspSafeMdlCreate`
  - `FspSafeMdlCopyBack`
  - `FspSafeMdlDelete`
- Cache-manager wrappers:
  - `FspCcInitializeCacheMap`
  - `FspCcSetFileSizes`
  - `FspCcCopyRead`
  - `FspCcCopyWrite`
  - `FspCcMdlRead`
  - `FspCcMdlReadComplete`
  - `FspCcPrepareMdlWrite`
  - `FspCcMdlWriteComplete`
  - `FspCcFlushCache`
- Security/EA helpers:
  - `FspQuerySecurityDescriptorInfo`
  - `FspEaBufferFromOriginatingProcessValidate`
  - `FspEaBufferFromFileSystemValidate`
- Notification/oplock wrappers:
  - `FspNotifyInitializeSync`
  - `FspNotifyFullChangeDirectory`
  - `FspNotifyFullReportChange`
  - `FspOplockBreakH`
  - `FspCheckOplock`
  - `FspCheckOplockEx`
  - `FspOplockFsctrl`
- Work-item helpers:
  - `FspInitializeSynchronousWorkItem`
  - `FspExecuteSynchronousWorkItem`
  - `FspExecuteSynchronousWorkItemRoutine`
  - `FspInitializeDelayedWorkItem`
  - `FspQueueDelayedWorkItem`
  - `FspQueueDelayedWorkItemDPC`
- IRP hook helpers:
  - `FspIrpHook`
  - `FspIrpHookReset`
  - `FspIrpHookContext`
  - `FspIrpHookNext`
- Unicode compare helpers:
  - `FspUpcaseAscii`
  - `FspCompareUnicodeString`

## Version and Object Utilities

`FspIsNtDdiVersionAvailable`:

- Caches the computed OS version.
- Uses `RtlGetVersion`.
- Builds an NTDDI-style value.
- Maps Windows 10 build numbers to subversions with binary search.
- Uses `InterlockedExchange` for benign thread-safe caching.

`FspGetDeviceObjectPointer` progressively extends a partial object name component by component, trying `IoGetDeviceObjectPointer` and validating intermediate directory or symbolic-link objects.

`FspRegistryGetValue` opens a registry key and queries one value, treating `STATUS_BUFFER_OVERFLOW` from `ZwQueryValueKey` as success.

## Internal IRP Sending

The send helpers allocate their own IRPs, fill one stack location, set a completion routine, call the target driver, wait if pending, and return the captured `IO_STATUS_BLOCK`.

They are used for:

- setting allocation/EOF information,
- querying security,
- querying EAs,
- sending Mount Manager buffered device-control requests.

The common completion routine copies `Irp->IoStatus`, signals an event, frees the IRP, and returns `STATUS_MORE_PROCESSING_REQUIRED`.

## User Buffer Handling

`FspBufferUserBuffer`:

- Handles zero length and already-buffered IRPs as success.
- Reuses kernel system buffers for kernel-mode system-range buffers.
- Otherwise allocates a nonpaged system buffer.
- Copies input for `IoReadAccess`; zeroes output buffers otherwise.
- Sets buffered I/O flags so I/O manager cleanup/copyback behavior applies.

`FspLockUserBuffer`:

- Allocates an MDL over `Irp->UserBuffer`.
- Probes and locks pages with exception handling.
- Stores the MDL in `Irp->MdlAddress`.

`FspMapLockedPagesInUserMode` wraps `MmMapLockedPagesSpecifyCache` with exception handling.

## Cache Manager Wrappers

The `FspCc*` functions wrap cache-manager calls in structured exception handling and return `NTSTATUS` rather than propagating exceptions. `FspCcCopyRead` and `FspCcCopyWrite` convert a false cache-manager return to `STATUS_PENDING`.

## Security and EA Validation

`FspQuerySecurityDescriptorInfo` wraps `SeQuerySecurityDescriptorInfo`, maps expected user-buffer exceptions to `STATUS_INVALID_USER_BUFFER`, and converts `STATUS_BUFFER_TOO_SMALL` to `STATUS_BUFFER_OVERFLOW`.

`FspEaBufferFromOriginatingProcessValidate`:

- Calls `IoCheckEaBufferValidity`.
- Validates every EA name with `FspEaNameIsValid`.
- Reports invalid EA offset.

`FspEaBufferFromFileSystemValidate`:

- Allows zero-length EA buffers.
- Normalizes the final EA's `NextEntryOffset` to zero before validation because user-mode filesystems may return a final nonzero offset.

## Safe MDL Logic

`FspSafeMdlCheck` returns true only when the MDL begins and ends on page boundaries.

`FspSafeMdlCreate` builds a replacement MDL that is safe to map to user mode:

- Gets a system address for the original MDL.
- Allocates a new MDL with copied PFN array.
- Detects unaligned first and last pages.
- Allocates nonpaged page buffers for edge pages.
- For input/read access, copies original edge-page data and zero-fills unused page portions.
- For output/write access, zeroes edge pages.
- Replaces first/last PFNs with the safe buffer PFNs.

`FspSafeMdlCopyBack` copies modified edge-page data back to the original user MDL for write operations.

`FspSafeMdlDelete` frees edge buffers, the replacement MDL, and the wrapper.

## IRP Completion Hooks

`FspIrpHook` replaces the current stack completion routine while preserving the prior routine/context/control flags in an allocated hook context when needed.

`FspIrpHookReset` restores or clears the completion routine.

`FspIrpHookNext` invokes the preserved completion routine if its original invoke flags match the final IRP state, otherwise propagates pending state. It frees the hook context.

## Unicode Comparison

`FspCompareUnicodeString` performs a fast ASCII path:

- Compares length first.
- For case-insensitive comparison, uses bit-twiddling ASCII upcase.
- Falls back to `RtlCompareUnicodeString` if either character is non-ASCII.
- In debug builds, compares the sign of the optimized result against `RtlCompareUnicodeString`.

## Notable Details

- Must-succeed allocation loops retry forever with increasing short delays.
- Many wrappers are paged, but completion and DPC routines are explicitly marked nonpaged by comments and omitted from alloc pragmas.
- The safe-MDL implementation is central to avoiding exposure of unrelated data in partially covered pages mapped to user mode.
