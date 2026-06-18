# File Research: sources/windows/reactos/drivers/filesystems/cdfs/pnp.c

Handles Plug and Play IRPs delivered to CDFS volume device objects, including query-remove, remove, surprise-remove, and cancel-remove.

Key entry points:
- `CdCommonPnp()` validates the target as a CDFS volume device object, forces synchronous handling, finds the VCB, dispatches known minor functions, and passes unknown requests down the stack.
- `CdPnpQueryRemove()` locks the volume, sends the query down synchronously, and starts forced dismount if lower drivers accept removal.
- `CdPnpRemove()` unlocks or invalidates the volume, passes the remove IRP down, then forces dismount.
- `CdPnpSurpriseRemove()` marks the VCB invalid immediately, passes surprise removal down, then attempts dismount.
- `CdPnpCancelRemove()` reverses a prior query-remove by unlocking the volume and passing the cancel down.
- `CdPnpCompletionRoutine()` signals a stack-local event and returns `STATUS_MORE_PROCESSING_REQUIRED` so the caller can finish synchronously.

Core mechanics:
- PnP requests have no file object, so the VCB is recovered from the volume device object.
- `CdData.DataResource` serializes PnP handling against mount, verify, and teardown paths.
- Query/remove/surprise paths copy the current stack location, install a completion event, call the target device, and wait for completion when pending.
- Query-remove keeps a temporary VCB reference while dropping and reacquiring locks around `CdLockVolumeInternal()`.
- Successful query-remove depends on CDFS internal streams closing and dropping their target-device references.

Important invariants:
- `IRP_CONTEXT_FLAG_WAIT` is set so all PnP work is synchronous.
- If the VCB has already been disconnected (`Vpb == NULL`), the request is passed through.
- Query-remove may fail with `STATUS_DEVICE_BUSY` if dismount began but references still remain.
- Surprise-remove has no recovery path; it marks the VCB invalid.

Filesystem relevance:
- Coordinates volume teardown with Windows storage-stack device removal.
- Protects CDFS from stale volume access after media/device removal.

Notable risks:
- Query-remove correctness depends on subtle reference-count behavior of internal stream file objects and outside holders such as tracing components.
- Pass-through uses `Vcb->TargetDeviceObject`; the code relies on the VCB still being valid for the pass-through path after validation.
