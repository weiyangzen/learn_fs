# File Research: sources/os/linux/linux-stable/fs/gfs2/inode.h

## Scope

This header declares inode-facing GFS2 helpers, small inline inode predicates/accounting helpers, file operation exports, and file attribute APIs.

## APIs And Helpers

- Declares folio/internal read/address-space helpers: `gfs2_release_folio()`, `gfs2_internal_read()`, `gfs2_set_aops()`.
- Inline predicates: `gfs2_is_stuffed()`, `gfs2_is_jdata()`, `gfs2_is_ordered()`, `gfs2_is_writeback()`, `gfs2_is_dir()`.
- Block accounting helpers: `gfs2_set_inode_blocks()`, `gfs2_get_inode_blocks()`, `gfs2_add_inode_blocks()`.
- Identity helpers: `gfs2_check_inum()`, `gfs2_inum_out()`, `gfs2_check_internal_file_size()`.
- Declares inode lookup and namespace helpers: `gfs2_setup_inode()`, `gfs2_inode_lookup()`, `gfs2_lookup_by_inum()`, `gfs2_dinode_dealloc()`, `gfs2_lookupi()`, `gfs2_lookup_meta()`.
- Declares `gfs2_permission()`, `gfs2_dinode_out()`, `gfs2_open_common()`, `gfs2_seek_data()`, `gfs2_seek_hole()`.
- Exports file operation tables, mapping DLM-disabled builds to nolock tables.
- Declares file attribute helpers and `gfs2_set_inode_flags()`.
- Defines `gfs2_localflocks()` based on DLM build support and mount arguments.

## Dependencies And Role

- Included by file, inode, glops, and other GFS2 files needing inode state predicates, VFS op tables, and lookup/permission helpers.
- Bridges inode implementation with file operations and build-time DLM configuration.

## Risks And Invariants

- `gfs2_is_stuffed()` relies on `i_height == 0` as the inline-data marker.
- Block accounting shifts between filesystem blocks and sectors; callers must pass block counts, not byte counts.
- `gfs2_check_internal_file_size()` enforces internal file size alignment and withdraws/marks consistency errors through `gfs2_consist_inode()`.
- Build-time DLM conditionals change exported operation tables; callers should use the public names rather than assuming lock support.
