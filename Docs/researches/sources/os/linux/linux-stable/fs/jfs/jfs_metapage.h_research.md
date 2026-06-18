# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_metapage.h

## Role

Declares `struct metapage`, metapage flags, public metapage operations, convenience wrappers, and invalidation macros.

## Key Definitions

- `struct metapage` begins with the same log sync prefix shape used by `struct logsyncblk`, then stores flags, reference count, data pointer, block index, wait queue, folio, superblock, logical size, commit LSN, `nohomeok`, and journal pointer.
- Public flags include `META_locked`, `META_dirty`, `META_sync`, `META_discard`, `META_forcewrite`, and `META_io`.
- `read_metapage()` and `get_metapage()` wrap `__get_metapage()` for existing versus newly allocated metadata.
- `write_metapage()`, `flush_metapage()`, and `discard_metapage()` are inline state transitions followed by release.
- `metapage_nohomeok()` pins the folio and marks metadata dirty so journal ordering can prevent unsafe home writes.
- `_metapage_homeok()` and `metapage_homeok()` reverse `nohomeok` once journal commit ordering permits home writeback.
- `metapage_wait_for_io()` serializes against home I/O for logsync-list operations.
- `invalidate_pxd_metapages`, `invalidate_dxd_metapages`, and `invalidate_xad_metapages` map extent descriptors to `__invalidate_metapages()` calls.

## Design Notes

The header exposes the core ordering mechanism used by the transaction manager: metadata is held `nohomeok` while journal records are pending, then released homeward after commit.
