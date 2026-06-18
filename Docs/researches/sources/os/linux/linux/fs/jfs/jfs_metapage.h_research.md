# File Research: sources/os/linux/linux/fs/jfs/jfs_metapage.h

Declares the JFS metapage abstraction and helper APIs used throughout metadata, transaction, and log code.

`struct metapage` begins with the same logsync prefix layout as `struct logsyncblk`, allowing metapages to be linked directly into `jfs_log.synclist`. It then stores flag bits, reference count, data pointer, block index, wait queue, backing folio, superblock, logical size, committed LSN, no-home-write counter, and owning log pointer.

Flags:
- `META_locked`: per-metapage lock.
- `META_dirty`: metadata needs writeback.
- `META_sync`: write synchronously on release.
- `META_discard`: page should not be reused/written.
- `META_forcewrite`: override `nohomeok`.
- `META_io`: writeback in progress.

Exports:
- Lifecycle: `metapage_init`, `metapage_exit`.
- Acquisition: `read_metapage()`, `get_metapage()`, `__get_metapage()`.
- Release/write helpers: `release_metapage`, `grab_metapage`, `force_metapage`, `write_metapage`, `flush_metapage`, `discard_metapage`.
- Transaction coordination: `metapage_nohomeok`, `metapage_homeok`, `_metapage_homeok`, `metapage_wait_for_io`.
- Extent invalidation helpers for PXD, DXD, and XAD descriptors.

Integration:
- Exposes `jfs_metapage_aops` for metadata inode mappings.
- The inline helpers encode the critical journal invariant that home writes are blocked while `nohomeok` is nonzero.
