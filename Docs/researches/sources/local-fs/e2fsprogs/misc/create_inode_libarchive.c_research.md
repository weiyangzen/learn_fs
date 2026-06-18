# File Research: sources/local-fs/e2fsprogs/misc/create_inode_libarchive.c

## Purpose
Implements the libarchive-backed tarball population path for e2fsprogs filesystem creation helpers. Its exported entry point is `__populate_fs_from_tar`, which reads an archive and creates corresponding ext2/3/4 inodes under a target root.

## Main Behaviors
- Supports three build modes:
  - Disabled libarchive: provides a stub `__populate_fs_from_tar` returning `ENOTSUP`.
  - `CONFIG_DLOPEN_LIBARCHIVE`: loads `libarchive.so.13` or platform equivalent at runtime and resolves required symbols manually.
  - Direct libarchive linkage: assigns libarchive functions to local function pointers.
- Walks archive entries with `archive_read_next_header`.
- Resolves parent directories using `__find_path`, which iteratively looks up slash-separated components from a root inode.
- Handles repeated archive entries by unlinking and freeing the existing non-directory inode before recreating it.
- Creates archive entry types:
  - Regular files through `do_write_internal_tar`.
  - Directories through `do_mkdir_internal`.
  - Symlinks through `do_symlink_internal`.
  - Character/block/FIFO/socket nodes through `do_mknod_internal`.
  - Hardlinks by resolving the archive hardlink target and calling `add_link`.
- Applies inode metadata with `set_inode_extra`.
- Copies selected xattrs unless `POPULATE_FS_NO_COPY_XATTRS` is set.

## Important Functions
- `libarchive_available`: validates/initializes libarchive function pointers.
- `__find_path`: translates a path relative to an ext2 root inode into an inode number.
- `remove_inode`: decrements link count and frees blocks/xattrs when link count reaches zero.
- `copy_file_chunk_tar`: streams archive file data into an `ext2_file_t`, skipping zero blocks for sparse-friendly writes.
- `copy_file_tar`: opens the ext2 file, allocates a 16 MiB copy buffer and zero buffer, then copies file contents.
- `do_write_internal_tar`: allocates a new inode, links it, initializes mode/timestamps/size/extents/inline-data, then writes contents.
- `set_inode_xattr_tar`: copies only `security.capability` and `gnu.translator` xattrs into ext2 xattr storage.
- `handle_entry`: dispatches archive entries by file type.
- `__populate_fs_from_tar`: top-level archive open/read/create/metadata loop.

## Dependencies
- Local e2fsprogs helpers from `create_inode.h`, including inode creation, symlink, mknod, link, and metadata helpers.
- `ext2fs` inode, xattr, file, bitmap, and block-punch APIs.
- Optional libarchive headers or runtime-loaded libarchive symbols.
- Global `link_append_flag`.

## Notes and Edge Cases
- The file can compile without `archive.h` by using opaque libarchive declarations.
- Sparse file support is implemented by avoiding writes of all-zero filesystem blocks.
- Existing directories in duplicate tar entries are preserved; existing non-directories are removed and recreated.
- Error handling commonly returns `1` for archive/libarchive failures rather than a specific libext2fs error code.
- The cleanup path unconditionally calls archive close/free after `a` creation path; failures before reader creation are guarded by flow but the function assumes `a` exists once past allocation.
