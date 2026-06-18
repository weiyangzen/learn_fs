# File Research: sources/os/linux/linux-stable/fs/nfsd/blocklayout.c

Purpose: Implements NFSD pNFS block and SCSI layout operations.

Key responsibilities:
- Maps filesystem extents with `s_export_op->map_blocks` and translates iomap types into pNFS block extent states.
- Handles layoutget:
  - rejects requests during grace,
  - requires block-aligned offsets,
  - enforces client `lg_maxcount`,
  - caps allocation at one page,
  - builds an extent array,
  - validates `lg_minlength`.
- Handles layoutcommit by decoding client layout updates and calling `s_export_op->commit_blocks` with mtime/size attributes.
- For block layout:
  - returns simple block device volume identity via exportfs UUID.
- For SCSI layout:
  - obtains unique disk designator,
  - registers and reserves persistent reservation key,
  - tracks client/device fencing in an xarray,
  - fences clients with PR preempt when recalls fail.
- Exports `bl_layout_ops` and `scsi_layout_ops`.

Integration:
- Depends on exportfs block operations, iomap, NFSD pNFS layout core, filecache, VFS helpers, and tracepoints.
- Uses `locks_in_grace` from `fs/nfs_common/grace.c`.
- Pairs with XDR helpers in `blocklayoutxdr.c`.

Risks and notes:
- Device IDs are advertised with notification flags to encourage Linux client caching despite RFC ambiguity.
- SCSI fencing carefully avoids infinite retry when a PR preempt may already have reached the device.
- Partitions are rejected for getdeviceinfo.
