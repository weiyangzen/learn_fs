# File Research: sources/windows/dokany/sys/dokan.c

## Role

Core Dokan driver initialization and shared kernel utilities. It sets driver dispatch tables, Fast I/O callbacks, lookaside lists, filesystem filter callbacks, lock debugging, oplock debugging, change notification helpers, MDL helpers, and global cleanup.

## Main Areas

- Driver lifecycle:
  - `DriverEntry`
  - `DokanUnload`
  - `CleanupGlobalDiskDevice`
  - `InitMultiVersionResources`
- Fast I/O and cache callbacks:
  - `DokanFastIoCheckIfPossible`
  - `DokanFastIoRead`
  - `DokanAcquireForCreateSection`
  - `DokanReleaseForCreateSection`
  - `DokanAcquireForCcFlush`
  - `DokanReleaseForCcFlush`
  - `DokanFilterCallbackAcquireForCreateSection`
- Allocation helpers:
  - `DokanLookasideCreate`
- Notification:
  - `DokanNotifyReportChange0`
  - `DokanNotifyReportChange`
- Request/context helpers:
  - `DokanCheckCCB`
  - `IsCcbAndDcbSameMount`
  - `DokanAllocateMdl`
  - `DokanFreeMdl`
  - `PointerAlignSize`
- Lock debugging:
  - `DokanLockWarn`
  - `DokanLockNotifyResolved`
  - `DokanResourceLockWithDebugInfo`
  - `DokanResourceUnlockWithDebugInfo`
  - `DokanVCBTryLockRW`
- Oplock debugging:
  - `GetOplockControlDebugInfoBit`
  - `OplockDebugRecord*`
- Misc:
  - `DokanDispatchShutdown`
  - `DokanNoOpAcquire`
  - `DokanNoOpRelease`
  - `DokanCheckOplock`
  - `DokanCompleteIrpRequest`
  - `RunAsSystem`

## Driver Initialization

`DriverEntry`:

- Creates global disk device.
- Assigns all supported `MajorFunction` entries to `DokanBuildRequest`.
- Initializes Fast I/O dispatch:
  - Uses FsRtl copy read/write and MDL helpers.
  - Hooks section and cache flush acquisition/release.
- Initializes version-dependent resources and optional FsRtl routine pointers.
- Initializes IRP entry and CCB/FCB/ERESOURCE lookaside lists.
- Registers filesystem filter callbacks.
- Detects whether reparse mount-point filename repair is needed.

## Notifications

`DokanNotifyReportChange0`:

- Converts stream notifications when filenames contain `:`.
- Computes filename offset after the final backslash.
- Calls `FsRtlNotifyFullReportChange`.
- Catches access violations around notification state and logs structured errors.

## Locking

The file provides debug-aware ERESOURCE acquisition:

- Repeatedly attempts nonblocking acquisition.
- Emits periodic warnings after long waits.
- Tracks exclusive owner thread and call site.
- Clears debug owner state on final unlock.

## Dependencies

- `dokan.h`
- `util/str.h`
- `mountmgr.h`
- Windows kernel FsRtl, cache manager, object/thread, and resource APIs.

## Notes and Risks

- Fast I/O mostly delegates to FsRtl cache helpers or returns false.
- Notification exception handlers suggest rare real-world invalid notify-list/file-name cases.
- `RunAsSystem` creates a system thread and waits synchronously.
- Lock debug mode can materially change acquisition behavior by polling and logging.
