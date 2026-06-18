# File Research: sources/local-fs/xfsprogs/libxfs/xfs_log_format.h

## Role

This header defines XFS on-disk log record formats and all log item format structures interpreted by recovery. It covers physical log record headers, transaction headers, log item type codes, inode and buffer log formats, deferred intent/done formats, quota log formats, inode creation records, deferred attribute formats, and quota status flags.

## Physical Log Format

The file defines:

- log record size/version constants
- log cycle and LSN helpers
- log clients and unmount record type
- log operation header flags for start, commit, continuation, end, and unmount transactions
- log record host format codes
- `struct xlog_rec_header`
- `struct xlog_rec_ext_header`

The log record header includes magic, cycle, version, length, LSNs, CRC, previous block, operation count, cycle data, format, filesystem UUID, v2 size, compatibility padding, and extension headers. The comments preserve historic i386 checksum compatibility rules.

## Transaction And Item Types

`struct xfs_trans_header` identifies transaction type and item count. CIL-enabled logs use `XFS_TRANS_CHECKPOINT`.

The `XFS_LI_*` constants identify log items for extents, inode unlink, inode, buffers, dquots, quotaoff, inode create, reverse map intents, refcount intents, bmap intents, attr intents, mapping exchange intents, and realtime variants. `XFS_LI_TYPE_DESC` maps them to names.

## Inode Logging

`struct xfs_inode_log_format` describes an inode item in the log, including fields logged, fork data/root sizes, inode number, device id union, inode buffer block, length, and offset. A packed 32-bit compatibility variant is defined.

`XFS_ILOG_*` flags identify logged inode core, data fork local data, data fork extents, data btree root, device, attr local data, attr extents, attr root, replay owner changes, and in-memory-only timestamp/version triggers.

`struct xfs_log_dinode` mirrors `struct xfs_dinode` in host order for logging. It includes legacy and v3 inode fields, large extent counter unions, next-unlinked pointer, CRC/change count/LSN/flags2, CoW or used-blocks union, creation time, inode number, and UUID.

## Buffer Logging

`struct xfs_buf_log_format` describes a logged buffer and a dirty bitmap of 128-byte chunks. Flags identify inode buffers, canceled freed buffers, and dquot buffers.

`enum xfs_blft` stores buffer type information in the upper bits of `blf_flags` so recovery can find magic fields and recompute CRCs after replay. Inline helpers encode and decode that type.

## Deferred Intent Formats

The header defines shared extent payload structures and log formats for:

- EFI/EFD extent free intents and done items, including 32-bit and 64-bit alignment variants
- RUI/RUD reverse mapping intents and done items
- CUI/CUD refcount update intents and done items
- BUI/BUD bmap update intents and done items
- XMI/XMD mapping exchange intents and done items

Flag masks encode operation type in low bits and fork/unwritten/realtime/shared metadata in high bits. Size helper functions compute variable-length intent item sizes.

## Quota And Inode Create Formats

`struct xfs_dq_logformat` logs a dquot location. `struct xfs_qoff_logformat` logs quotaoff operations. The header also defines quota accounting, enforcement, and checked bits stored in mount and superblock quota flags.

`struct xfs_icreate_log` records inode chunk initialization during inode allocation.

## Attribute Intent Format

The file defines deferred attr operation flags for set, remove, replace, and parent pointer set/remove/replace. `XFS_ATTRI_FILTER_MASK` limits persisted attr filter bits. `struct xfs_attri_log_format` records attr operation id, inode, generation for parent pointer ops, operation flags, name lengths, value length, and filter. `struct xfs_attrd_log_format` completes the intent.

## Invariants

- Many log item structures require the first fields to be type and size fitting in 32 bits because recovery relies on that.
- Structures are append-only from a format compatibility perspective.
- Several logged structures carry host-order fields for historical reasons.
- Variable-length intent records require exact size calculations for recovery parsing.
- Inode log dinode must remain layout-compatible with the dinode core definition except endianness annotations.

## Dependencies

This header is consumed by transaction logging, log recovery, inode flushing, buffer item logging, deferred operation recovery, quota code, and on-disk layout checks.

## Research Notes

This is a format contract, not just a local header. Any structure size, offset, flag, or type-code change affects recovery compatibility and must be mirrored in layout assertions and replay code.
