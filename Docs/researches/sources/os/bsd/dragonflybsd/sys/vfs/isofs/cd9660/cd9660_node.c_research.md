# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_node.c

## Scope

Implements ISO9660 in-core node cache management, vnode inactive/reclaim handling, default ISO extended attribute interpretation, timestamp conversion, and directory-record-to-inode-number derivation.

## APIs And Behavior

- `cd9660_init()` sizes and allocates the global `iso_node` hash table, capped at `CD9660_HASH_SIZE_LIMIT`.
- `cd9660_uninit()` frees the hash table.
- `cd9660_ihashget()` looks up an in-core ISO node by device and inode number, locks the vnode with `vget()`, and revalidates the hash after blocking.
- `cd9660_ihashins()` inserts a node if no active duplicate exists.
- `cd9660_reclaim()` removes the node from the hash, releases the device vnode, and frees the `iso_node`.
- `cd9660_inactive()` clears flags and recycles vnodes with missing or zero mode state.
- `cd9660_defattr()` derives default file type, permissions, UID, GID, and link count from directory records and optional ISO extended attributes.
- `cd9660_deftstamp()`, `cd9660_tstamp_conv7()`, and `cd9660_tstamp_conv17()` convert ISO 7-byte and 17-byte timestamps into `timespec`.
- `isodirino()` builds the pseudo-inode number from extent plus extended-attribute length shifted by the mount block size.

## Dependencies

Uses DragonFly vnode locking/reference APIs, `lwkt_token` for hash serialization, buffer reads through `cd9660_devblkatoff()`, ISO numeric helpers from `iso.h`, and allocation types declared by the CD9660 VFS layer.

## Risks And Invariants

Hash lookup must revalidate after `vget()` because reclaim can remove the node while the caller blocks. Timestamp conversion assumes valid decimal fields in 17-byte timestamps. Extended attributes are optional and default to root ownership plus read/execute permissions when absent or invalid.
