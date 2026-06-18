# File Research: sources/os/linux/linux/fs/nfsd/blocklayout.c

Implements NFSD pNFS block and SCSI layout operations.

Key behavior:
- `nfsd4_block_map_extent()` maps file offsets to filesystem block extents through exportfs block ops and converts `iomap` types to pNFS block extent states.
- Handles read/write differences:
  - Mapped extents become read-only or read-write data depending on layout iomode.
  - Unwritten extents may become invalid-data layouts for write layouts.
  - Holes can be represented as no-data layouts for reads.
  - Unsupported/delalloc cases return layout unavailable.
- `nfsd4_block_proc_layoutget()` validates grace state, block alignment, client maxcount, allocates a bounded extent array, maps enough extents to satisfy requested/minimum length, and adjusts the returned layout segment to extent boundaries.
- Layout commit decodes client layout updates and passes iomaps to exportfs block `commit_blocks()`, optionally applying a new size.
- Block layout `GETDEVICEINFO` returns a simple volume using the backing block device UUID, rejecting partition exports.
- Registers `bl_layout_ops` for block layout getdeviceinfo, layoutget, layoutcommit, and encoding callbacks.
- SCSI layout support manages per-client device fence state in an xarray.
- SCSI device info obtains a disk unique identifier, registers/reserves persistent-reservation keys, and returns a SCSI volume with the client PR key.
- SCSI layout commit decodes SCSI layout updates and shares block commit logic.
- `nfsd4_scsi_fence_client()` preempts a client’s persistent reservation key after recall failure and records fenced state to avoid repeated fencing loops.
- Registers `scsi_layout_ops` with SCSI-specific getdeviceinfo, layoutcommit, and fence callbacks.

Important interactions:
- Depends on filesystem `s_export_op->block_ops` for block mapping, UUID retrieval, and commit.
- Uses NFSD pNFS layout operation tables consumed by the NFSv4.1 layout server.
- Uses grace-period tracking to reject layout grants during recovery.
