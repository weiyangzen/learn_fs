# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_remote.c

## Purpose

`xfs_attr_remote.c` manages out-of-line extended attribute values stored in blocks mapped by an inode's attr fork. It computes remote block requirements, verifies and stamps CRC-enabled remote value headers, reads and writes remote value buffers, finds allocation holes, allocates remote extents incrementally for delayed attr operations, invalidates cached remote buffers, and removes remote extents.

## Remote Buffer Rules

Remote attr value buffers are deliberately not logged. On CRC-enabled filesystems each remote buffer contains a header, and maximum-size values can require more than 64 KiB worth of buffer coverage. Because the log format cannot handle dirty buffers larger than `XFS_MAX_BLOCKSIZE`, this file writes remote buffers synchronously and uses `NULLCOMMITLSN` in CRC headers so log recovery ignores stale LSNs if blocks are later reused as logged metadata.

## Size and Header Helpers

- `xfs_attr3_rmt_buf_space` returns usable bytes per attr block, subtracting the CRC header only on CRC filesystems.
- `xfs_attr3_rmt_blocks` computes fsblocks required for a value. CRC filesystems divide by usable payload per block because each block has its own header.
- `xfs_attr3_rmt_hdr_set` stamps magic, offset, bytes, uuid, owner, physical block number, and `NULLCOMMITLSN`.
- `xfs_attr3_rmt_hdr_ok` and `xfs_attr3_rmt_verify` validate physical location, value offset, payload size, owner, uuid, magic, and xattr size bounds.

`xfs_attr3_rmt_buf_ops` provides read, write, and structural verifiers for remote value buffers.

## Read and Write Paths

`xfs_attr_rmtval_get` walks attr fork extents with `xfs_bmapi_read`, reads each physical buffer with remote buf ops, disambiguates disk `-ENODATA` to `-EIO`, copies payload out, and marks the attr fork sick on metadata corruption.

`xfs_attr_rmtval_set_value` assumes extents are already allocated. It maps the extents, gets buffers, stamps headers and copies payload via `xfs_attr_rmtval_copyin`, then writes each buffer synchronously with `xfs_bwrite`.

The copy helpers roll through multi-block buffers while updating value offset, remaining length, and source/destination pointers. The final partial block is zero-filled after the payload.

## Allocation and Removal

`xfs_attr_rmt_find_hole` finds an unused logical range in the attr fork large enough for the remote value and records it in `args->rmtblkno/rmtblkcnt`.

`xfs_attr_rmtval_find_space` initializes delayed intent remote-allocation state and stores the logical start/count in the attr intent.

`xfs_attr_rmtval_set_blk` allocates one extent with `xfs_bmapi_write`, updates the saved map, and advances `xattri_lblkno/xattri_blkcnt` so the caller can roll transactions between allocation steps.

`xfs_attr_rmtval_invalidate` maps each remote extent and marks any incore buffers stale before unmapping. `xfs_attr_rmtval_stale` requires exclusive inode lock and rejects delayed or hole mappings as corruption.

`xfs_attr_rmtval_remove` unmaps remote extents with `xfs_bunmapi`. It returns `-EAGAIN` when more unmapping remains so the attr state machine can roll the transaction and call again.

## Dependencies and Risks

This file depends on bmap read/write/unmap, buffer cache operations, attr geometry, transaction state supplied by callers, and filesystem health marking. The most sensitive invariants are that remote blocks never enter the log, CRC headers must match physical block/owner/offset/length, and the leaf entry must remain INCOMPLETE until allocation and synchronous writes are complete.
