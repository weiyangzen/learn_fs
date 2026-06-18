# File Research: sources/local-fs/e2fsprogs/misc/create_inode_libarchive.h

## Purpose
Declares the tarball population entry point implemented in `create_inode_libarchive.c`.

## API
- `__populate_fs_from_tar(ext2_filsys fs, ext2_ino_t root_ino, const char *source_tar, ext2_ino_t root, struct hdlinks_s *hdlinks, struct file_info *target, int flags, struct fs_ops_callbacks *fs_callbacks)`

## Dependencies
- Relies on types from surrounding `create_inode` and ext2fs headers included before or alongside this header.
- Exposes a low-level internal helper rather than a public installed API.

## Notes
- The declaration includes `hdlinks`, `target`, flags, and callback hooks to match the non-archive population interface, though the archive implementation ignores `hdlinks`.
