# File Research: sources/os/linux/linux/fs/xfs/scrub/xfile.h

Declares the xfile abstraction used by online scrub/repair staging structures.

Key elements:
- `struct xfile` wraps a single `struct file *`.
- Declares lifecycle functions `xfile_create` and `xfile_destroy`.
- Declares byte-oriented access functions `xfile_load`, `xfile_store`, `xfile_discard`, and `xfile_seek_data`.
- Defines `XFILE_MAX_FOLIO_SIZE` as the largest page-cache folio size.
- Defines `XFILE_ALLOC` for `xfile_get_folio`.
- Declares folio pin helpers `xfile_get_folio` and `xfile_put_folio`.
- `xfile_bytes` reports allocated bytes from inode `i_blocks`.

Dependencies:
- Requires Linux folio/file/inode types from surrounding kernel headers.
- Implemented by `scrub/xfile.c`.

Research notes:
- `xfile_get_folio` exposes locked folios directly, so users must obey lock/release discipline.
- `xfile_bytes` reports backing allocation, not logical file size.
