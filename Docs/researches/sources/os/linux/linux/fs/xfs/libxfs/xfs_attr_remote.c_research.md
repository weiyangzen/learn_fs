# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_remote.c

## Purpose
Implements storage, verification, reading, writing, invalidation, allocation, and removal of remote XFS extended attribute values stored in attr-fork data blocks outside leaf entries.

## Main Interfaces
- Sizing: `xfs_attr3_rmt_buf_space()`, `xfs_attr3_rmt_blocks()`.
- Buffer verification: `xfs_attr3_rmt_buf_ops`, read/write/struct verifiers.
- Value IO: `xfs_attr_rmtval_get()`, `xfs_attr_rmtval_set_value()`.
- Allocation/removal state helpers: `xfs_attr_rmtval_find_space()`, `xfs_attr_rmtval_set_blk()`, `xfs_attr_rmtval_invalidate()`, `xfs_attr_rmtval_remove()`, `xfs_attr_rmt_find_hole()`.
- Cache stale marking: `xfs_attr_rmtval_stale()`.

## Remote Format
On CRC-enabled filesystems, every remote value block contains an `xfs_attr3_rmt_hdr`, so usable payload per block is `attr_blksize - sizeof(header)`. The number of blocks is therefore not a simple byte-to-FSB conversion for v5 filesystems. Remote attr buffers are written synchronously and deliberately avoid the logging system because maximum-sized values plus headers can exceed the maximum loggable buffer size.

## Verification And Copying
Read verification checks CRCs, magic, UUID, block address, payload byte count, total offset bounds, and nonzero owner for each attr block in the buffer. Copy-out then checks owner, offset, size, and block number against the expected attr value stream before copying payload into the caller buffer. Copy-in stamps headers, sets `NULLCOMMITLSN`, copies payload, and zeroes unused tail bytes in the final block.

## Control Flow
`xfs_attr_rmtval_get()` walks attr-fork mappings with `xfs_bmapi_read()`, reads each mapped disk buffer with remote attr buffer ops, copies out payload, and converts disk `-ENODATA` to `-EIO` to avoid confusion with xattr-not-found semantics.

`xfs_attr_rmtval_find_space()` finds an unused attr-fork logical range large enough for the value and seeds the delayed intent allocation fields. `xfs_attr_rmtval_set_blk()` allocates mapped blocks one transaction at a time with `xfs_bmapi_write()`. After all blocks are allocated, `xfs_attr_rmtval_set_value()` synchronously writes the value to those blocks.

Removal first invalidates any incore buffers for the mapped range, then `xfs_attr_rmtval_remove()` unmaps extents with `xfs_bunmapi()`, returning `-EAGAIN` until the unmap operation reports completion.

## Integration Points
Called by leaf value lookup and high-level delayed attr set/remove operations. Depends on attr fork bmap read/write/unmap helpers, XFS buffer cache, remote attr buffer ops, inode health marking, and transaction context supplied by the attr state machine.

## Notable Behaviors
- Remote attr headers use `NULLCOMMITLSN` so log recovery ignores meaningless LSNs for synchronously written, non-logged buffers.
- Incore stale marking rejects delayed or hole mappings as corruption and marks the attr fork sick.
- Remote value write durability precedes clearing `XFS_ATTR_INCOMPLETE` in the leaf entry.
- Removal progress does not need a separate sub-state; it is inferred from `xfs_bunmapi()` returning not-done.

## Risks And Review Focus
- Remote buffers must not acquire log items; accidentally logging them can exceed log buffer limits.
- Header owner/offset/length checks are critical to detecting stale or misdirected remote value blocks.
- The CRC versus non-CRC sizing split must stay consistent with leaf entry `rmtblkcnt` calculations.
- `-ENODATA` translation is important because xattr callers use that errno for a different meaning.
