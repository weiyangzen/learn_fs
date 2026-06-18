# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_log_format.h

## Role
`xfs_log_format.h` defines the on-disk journal format for XFS: physical log record headers, transaction headers, log item type codes, and per-item format structures used by log writing and recovery.

## Main Format Areas
- Physical log constants define iclog counts, record sizes, log versions, header sizes, cycle fields, and LSN helpers.
- `struct xlog_rec_header` and `struct xlog_rec_ext_header` define physical log record headers, CRC fields, cycle data, format identifiers, filesystem UUID, and log v2 size fields.
- `struct xlog_op_header` defines per-region operation headers and continuation/commit/unmount flags.
- `struct xfs_trans_header` identifies checkpoint transactions and item counts.
- `XFS_LI_*` constants enumerate all log item types, including inode, buffer, dquot, quotaoff, icreate, extent free, rmap, refcount, bmap, attr, exchange-map, and realtime intent/done pairs.

## Log Item Structures
- `struct xfs_inode_log_format` and `_32` describe logged inode items, fork data sizes, inode location, and special device data.
- `struct xfs_log_dinode` mirrors `struct xfs_dinode` in host CPU format for journaled inode cores.
- `struct xfs_buf_log_format` records buffer identity, flags, length, and dirty 128-byte chunk bitmap.
- EFI/EFD structures log extent free intents and completions, with 32-bit and 64-bit compatibility extent layouts.
- RUI/RUD structures log reverse mapping operations using `struct xfs_map_extent`.
- CUI/CUD structures log refcount updates using `struct xfs_phys_extent`.
- BUI/BUD structures log bmap updates.
- XMI/XMD structures log file mapping exchange operations and completion.
- Dquot and quotaoff structures log quota metadata updates and quota-off sequencing.
- `struct xfs_icreate_log` logs inode chunk initialization.
- ATTRI/ATTRD structures log deferred attr and parent-pointer attr operations.

## Flags and Helpers
- `XFS_ILOG_*` flags identify which inode core/fork/device fields are logged; timestamp and iversion flags are in-memory-only.
- Buffer log flags identify inode buffers, canceled buffers, dquot buffers, and buffer type magic-offset classes.
- Intent flag masks define allowed rmap, bmap, refcount, exchange-map, and attr operation bits.
- `xfs_*_log_format_sizeof` helpers compute variable-length log item sizes.

## Data and Invariants
- Many structures are part of the persistent log ABI and cannot be reordered without recovery changes.
- Some log items carry host-order data for historical reasons; recovery code must decode compatibility variants.
- Physical log record checksum sizing has i386 compatibility handling through `XLOG_REC_SIZE` and `XLOG_REC_SIZE_OTHER`.
- Buffer dirty maps use explicit padding rules so 32-bit and 64-bit structure sizes remain consistent.
- Parent pointer attr operations reuse attr intent records with dedicated PPTR operation codes and old/new name length handling.

## Dependencies
This header is included by most XFS log, transaction, recovery, inode, quota, bmap, attr, and deferred-operation code. It is also checked by `xfs_ondisk.h`.

## Research Notes
This is an ABI file, not merely an internal header. Its central constraint is compatibility with existing logs across architectures and kernel versions.
