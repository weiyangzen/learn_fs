# File Research: sources/windows/windows-driver-samples/filesys/cdfs/pnp.c

## Purpose

Handles Plug and Play IRPs for mounted CDFS volumes: query remove, remove, surprise removal, and cancel remove.

## Main Entry Points

- `CdCommonPnp`
- `CdPnpQueryRemove`
- `CdPnpRemove`
- `CdPnpSurpriseRemove`
- `CdPnpCancelRemove`
- `CdPnpCompletionRoutine`

## Dispatch Behavior

`CdCommonPnp` locates the VCB from the volume device object, validates that the device object is a CDFS volume object, forces synchronous operation, and dispatches by PnP minor code. Unknown minor codes and already-torn-down volumes are passed through with `IoSkipCurrentIrpStackLocation`.

## Remove Paths

`CdPnpQueryRemove` acquires the VCB, temporarily references it, tries to lock the volume, passes the query to the lower device stack synchronously, then initiates forced dismount on success. If the VCB remains due to lingering references, it returns `STATUS_DEVICE_BUSY`.

`CdPnpRemove` unlocks the volume if previously locked, marks the VCB invalid if no lock existed, forwards the remove IRP synchronously, and forces dismount.

`CdPnpSurpriseRemove` immediately marks the VCB invalid, forwards the surprise removal synchronously, then attempts forced dismount.

`CdPnpCancelRemove` reacquires the VCB, unlocks any previous query-remove volume lock, releases the VCB, and passes the cancel request down without a completion routine.

`CdPnpCompletionRoutine` signals a stack event and returns `STATUS_MORE_PROCESSING_REQUIRED` so the caller can resume after synchronous lower-stack completion.

## Dependencies

Relies on global `CdData` locking, VCB exclusive acquisition, internal volume lock/unlock helpers, VCB condition updates, lower-device IRP forwarding, and `CdCheckForDismount`.
