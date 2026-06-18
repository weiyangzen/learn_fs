# File Research: sources/windows/reactos/drivers/filesystems/udfs/shutdown.cpp

## Purpose

`shutdown.cpp` implements UDFS shutdown notification handling. On system shutdown it walks mounted UDF volumes, closes delayed/system opens, stops media-eject waiters, performs dismount/flush sequencing, and marks volumes shut down/read-only.

## Main Runtime Paths

- `UDFShutdown()` is the dispatch entry point:
  - enters filesystem context with `FsRtlEnterFileSystem()`
  - sets top-level IRP state
  - allocates a UDF IRP context
  - calls `UDFCommonShutdown()`
  - handles exceptions through the standard UDF exception path
  - completes the IRP on allocation failure
- `UDFCommonShutdown()` performs the actual volume sweep:
  - allocates a `PREVENT_MEDIA_REMOVAL_USER_IN` buffer used by dismount/eject logic
  - acquires `UDFGlobalData.GlobalDataResource`
  - iterates `UDFGlobalData.VCBQueue`
  - for each VCB not already marked `UDF_VCB_FLAGS_SHUTDOWN`:
    - optionally disables delayed close with `UDF_VCB_FLAGS_NO_DELAYED_CLOSE`
    - temporarily releases the global resource to close system delayed files under the root directory
    - closes delayed items when `UDF_DELAYED_CLOSE` is enabled
    - reacquires the global resource
    - stops the eject waiter
    - acquires the VCB resource exclusively
    - calls `UDFDoDismountSequence(Vcb, Buf, FALSE)`
    - delays one second for removable media
    - marks the volume shut down and read-only

## Synchronization

The routine uses `GlobalDataResource` for VCB queue traversal and `VCBResource` for per-volume shutdown mutation. It intentionally releases and reacquires the global resource around delayed-close work because comments indicate delayed-close helpers avoid acquiring `DelayedCloseResource` when the global resource is already held.

## Integration

This file depends on global UDFS mount state (`UDFGlobalData.VCBQueue`), VCB flags, delayed-close helpers, eject-waiter control, and dismount sequencing implemented elsewhere.

## Notable Risks

- The code advances `Link` before doing work on the current VCB because shutdown may delete or mutate the current VCB.
- Resource release/reacquire during traversal means concurrent queue changes are expected; the implementation relies on the pre-captured next link and global locking discipline.
- Shutdown forces `UDF_VCB_FLAGS_VOLUME_READ_ONLY`, preventing later write activity on volumes that remain referenced.
