# File Research: sources/os/linux/linux-stable/fs/nilfs2/mdt.h

`mdt.h` declares NILFS metadata-file support. It defines `struct nilfs_mdt_info`, stored in `inode->i_private`, with metadata operation locking (`mi_sem`), per-blockgroup locks, entry sizing, persistent allocator cache, shadow mapping, and block grouping fields.

It also defines `struct nilfs_shadow_map`, used to hold shadow bmap/page-cache state and frozen buffers during metadata operations such as GC DAT shadowing. The header exposes block access and lifecycle operations: `nilfs_mdt_get_block`, `nilfs_mdt_find_block`, delete/forget/fetch-dirty helpers, init/clear/destroy, entry-size setup, and shadow-map save/restore/clear/freeze APIs.

The inline helpers establish key conventions: metadata-file inodes are identified by non-NULL `i_private`; metadata dirty state is tracked with `NILFS_I_DIRTY`; `nilfs_mdt_cno()` reads the filesystem checkpoint number from `the_nilfs`; and `nilfs_mdt_bgl_lock()` retrieves per-blockgroup lock pointers. `NILFS_MDT_GFP` uses reclaim, IO, and highmem allocation flags for metadata pages.

This header is foundational for `sufile.c`, cpfile/dat/ifile code, and segment construction. It abstracts metadata files as ordinary inodes with extra private state and shadow-copy support.
