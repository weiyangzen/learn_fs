# File Research: sources/os/linux/linux/fs/gfs2/inode.h

## Scope

Declares GFS2 inode helper APIs, inline inode/data-mode helpers, block-count helpers, lookup/create-related exports, seek helpers, file operation exports, and file-attribute hooks.

## APIs And Helpers

- Declares page/internal read/address-space helpers: `gfs2_release_folio()`, `gfs2_internal_read()`, `gfs2_set_aops()`.
- Inline helpers classify inode/data state: `gfs2_is_stuffed()`, `gfs2_is_jdata()`, `gfs2_is_ordered()`, `gfs2_is_writeback()`, `gfs2_is_dir()`.
- Block helpers convert between GFS2 block counts and VFS sector-based `i_blocks`: `gfs2_set_inode_blocks()`, `gfs2_get_inode_blocks()`, `gfs2_add_inode_blocks()`.
- Identity helpers: `gfs2_check_inum()`, `gfs2_inum_out()`, `gfs2_check_internal_file_size()`.
- Declares inode lookup and permission APIs used outside `inode.c`.
- Declares `gfs2_open_common()`, `gfs2_seek_data()`, `gfs2_seek_hole()`, and fileattr functions implemented in `file.c`.
- Exports DLM and nolock file operation tables, with compile-time selection for single-node builds.

## Invariants

- `gfs2_is_stuffed()` treats height zero as inline/stuffed data.
- `gfs2_check_internal_file_size()` enforces min/max and block alignment for internal metadata files and reports inode consistency errors on failure.
- `gfs2_localflocks()` returns mount option state under DLM builds and always local-locking in single-node builds.
