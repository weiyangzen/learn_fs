# File Research: sources/windows/winfsp/src/sys/cleanup.c

Handles `IRP_MJ_CLEANUP` for control, virtual, and volume devices.

Device variants:
- `FspFsctlCleanup()` deletes a volume when the control file object has `FsContext2`.
- `FspFsvrtCleanup()` is a no-op success path.
- `FspFsvolCleanup()` performs real per-open cleanup for volume file objects.

Volume cleanup flow:
- Ignores invalid/uninitialized file objects.
- Acquires file-node main lock exclusively.
- Calls `FspFileNodeCleanup()` and decodes cleanup flags:
  - delete pending,
  - allocation-size reset,
  - file modified.
- Sends directory delete-pending/cleanup notifications through notify support.
- Removes byte-range locks for the file object/process.
- Creates a must-succeed user-mode `Cleanup` request.
- Populates cleanup metadata update flags for archive bit and times based on file object and descriptor state.
- Acquires paging I/O lock, assigns request ownership, stores IRP in request context, and flushes cleanup state.
- Posts best-effort if needed; otherwise completes locally and lets request finalizer do the mandatory teardown.

Completion/finalization:
- `FspFsvolCleanupComplete()` sends remove/modify notifications and invalidates parent directory or stream info caches as needed.
- `FspFsvolCleanupRequestFini()` always runs cleanup post-processing, even if user-mode disappears:
  - releases paging owner,
  - completes file-node cleanup,
  - checks oplocks,
  - sets `FO_CLEANUP_COMPLETE`,
  - detaches main file handle,
  - releases main owner,
  - closes main file handle.

Important semantic point:
- Cleanup cannot fail from the I/O manager perspective, so the code uses must-succeed request allocation and best-effort posting.
