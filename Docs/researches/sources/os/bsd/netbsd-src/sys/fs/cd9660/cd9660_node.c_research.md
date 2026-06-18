# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_node.c

## Summary
Implements CD9660 node pool lifecycle, inactive/reclaim operations, default attribute/timestamp extraction, ISO timestamp conversion, and ISO directory-record inode-number construction.

## Main Responsibilities
- Initialize and destroy `cd9660_node_pool` and ISO mount malloc type.
- Mark inactive nodes recyclable when mode is zero.
- Reclaim vnodes by destroying genfs node state and returning `iso_node` objects to the pool.
- Derive default file type, permissions, link count, uid, and gid from ISO directory records and optional extended attributes.
- Derive timestamps from extended attributes or directory record 7-byte dates.
- Convert 7-byte and 17-byte ISO timestamps to `timespec`.
- Compute directory inode numbers from extent and extended attribute length.

## Key Interfaces
- `cd9660_init()`, `cd9660_done()`.
- `cd9660_inactive()`, `cd9660_reclaim()`.
- `cd9660_defattr()`, `cd9660_deftstamp()`.
- `cd9660_tstamp_conv7()`, `cd9660_tstamp_conv17()`.
- `isodirino()`.

## Risks
Extended attribute parsing is conditional and falls back to permissive read/execute defaults. Timestamp timezone offsets are treated as unreliable outside a bounded range. `isodirino()` must remain inverse-compatible with vnode loading code.
