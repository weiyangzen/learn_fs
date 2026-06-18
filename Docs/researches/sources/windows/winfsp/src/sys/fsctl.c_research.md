# File Research: sources/windows/winfsp/src/sys/fsctl.c

## Role

Implements `IRP_MJ_FILE_SYSTEM_CONTROL` dispatch for both the WinFsp control device and mounted filesystem volume devices. It routes private WinFsp FSCTLs, mount/volume operations, reparse point operations, oplocks, statistics, persistent volume state, and retrieval pointers.

## Control Device Path

`FspFsctlFileSystemControl` handles the fsctl/control device:

- Mount-device and mount-manager setup.
- Volume name and volume list queries.
- Transaction FSCTLs: normal, batch, and internal.
- Stop/stop0 shutdown sequencing.
- Notifications.
- Driver unload.
- Extension-provider FSCTLs in the private control-code range.
- Mount-volume minor function.

The STOP/STOP0 comment documents an important protocol change: `FSP_FSCTL_STOP0` stops the IOQ without canceling active IRPs, allowing dispatcher threads to drain before `FSP_FSCTL_STOP` cancels remaining IRPs.

## Volume Device Path

`FspFsvolFileSystemControl` handles mounted volume FSCTLs:

- Work queue FSCTLs: `FSP_FSCTL_WORK`, `FSP_FSCTL_WORK_BEST_EFFORT`.
- Query WinFsp / `FSCTL_IS_VOLUME_MOUNTED`.
- Reparse point get/set/delete.
- Oplock requests and acknowledgements.
- `FSCTL_QUERY_PERSISTENT_VOLUME_STATE`.
- `FSCTL_FILESYSTEM_GET_STATISTICS`.
- `FSCTL_GET_RETRIEVAL_POINTERS`.

## Reparse Points

`FspFsvolFileSystemControlReparsePoint` validates volume support, file-object validity, buffers, access rights, and reparse payloads. For set/delete it validates the input reparse data, enforces write-related access, optionally checks symlink privilege when requested by volume parameters, and computes `TargetOnFileSystem` for absolute symlink targets that point back into the same filesystem. It then posts `FspFsctlTransactFileSystemControlKind` with the file name and input buffer.

For get, it validates output buffer presence and posts a read request under shared full locking. Completion validates the returned reparse buffer, ensures it fits, copies it to the caller buffer, and sets `IoStatus.Information`. Write completion invalidates file info and marks per-handle reparse/metadata flags.

## Oplocks

`FspFsvolFileSystemControlOplock` validates the file node and FSCTL buffers, acquires the file node exclusive for requests or shared for acknowledgements, computes the FSRTL oplock count source, blocks batch/filter/handle oplocks on delete-pending files, hooks the IRP completion, clears top-level IRP, and delegates to `FspFileNodeOplockFsctl`. FSRTL owns completion after this point, so the code returns with `FSP_STATUS_IGNORE_BIT`.

The completion hook queues a delayed work item that dereferences the volume device and frees the completion context. This compensates for the normal WinFsp completion path being bypassed by FSRTL-owned oplock IRPs.

## Other FSCTLs

`FspFsvolFileSystemControlQueryPersistentVolumeState` reports short-name creation disabled when the input request version and mask match expectations.

`FspFsvolFileSystemControlGetStatistics` copies volume statistics into the output buffer.

`FspFsvolFileSystemControlGetRetrievalPointers` provides a synthetic non-resident mapping: one extent with `Lcn = -1`, `NextVcn = AllocationSize / AllocationUnit`. It probes user buffers manually for the method-neither FSCTL and returns `STATUS_END_OF_FILE` when the starting VCN is beyond EOF.

## Completion And Finalization

`FspFsvolFileSystemControlComplete` ignores work FSCTLs with no `FileObject`, maps successful reparse completions to read/write helpers, then releases owner-held file-node locks. `FspFsvolFileSystemControlRequestFini` handles cancellation cleanup.

## Integration Points

This file connects user-mode transactions, `file.c` file-node locking/cache invalidation, `volume.c` control operations, FSRTL oplock APIs, MUP/provider checks for symlink target classification, and statistics helpers.

## Edge Cases And Risks

- Reparse-point symlink target classification has several MUP and volume-prefix branches and tolerates failures by leaving `TargetOnFileSystem` zero.
- Oplock IRPs intentionally bypass normal completion and require the hook/work-item cleanup path.
- Retrieval-pointers support is compatibility-oriented, not real allocation mapping.
