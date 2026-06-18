# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/xfile.h

## Purpose

Declares the `xfile` scrub staging-file API.

## Key Contents

- `struct xfile`
  - wraps the backing `struct file`.
- Lifecycle:
  - `xfile_create`
  - `xfile_destroy`
- Byte-range access:
  - `xfile_load`
  - `xfile_store`
  - `xfile_discard`
  - `xfile_seek_data`
- Folio access:
  - `XFILE_ALLOC`
  - `xfile_get_folio`
  - `xfile_put_folio`
- Accounting:
  - `xfile_bytes` reports allocated storage from inode `i_blocks`.

## Invariants

`XFILE_MAX_FOLIO_SIZE` follows page-cache folio limits. Folio users must release locked folios with `xfile_put_folio`.
