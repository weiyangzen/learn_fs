# File Research: sources/local-fs/e2fsprogs/misc/create_inode.c

## Purpose
Creates and populates ext filesystem inodes from host files, directories, special files, symlinks, hardlinks, tar archives, xattrs, sparse extents, and selected file flags. Used by mke2fs population paths.

## Main Creation Helpers
- `add_link()` links an existing inode into a directory and increments link count.
- `set_inode_extra()` copies uid, gid, permissions, and atime/ctime/mtime, clamping fake-time future timestamps.
- `set_inode_xattr()` copies host extended attributes into ext2fs xattr handles when supported.
- `do_mknod_internal()` creates character/block devices, FIFOs, and sockets.
- `do_symlink_internal()` creates symlinks, expanding the parent directory on `EXT2_ET_DIR_NO_SPACE`.
- `do_mkdir_internal()` creates directories with copied flag subset.
- `do_write_internal()` creates a regular file inode, initializes inline-data/extents when appropriate, applies copyable flags, and copies content.

## File Copy Behavior
- Uses 64 KiB buffers.
- Attempts sparse-aware copy with `SEEK_DATA/SEEK_HOLE`, then FIEMAP, then full scan fallback.
- Skips all-zero filesystem blocks instead of writing them.
- When fs-verity support is available and requested, copies Merkle tree, descriptor/signature metadata, records descriptor size, resets logical file size, and sets `EXT4_VERITY_FL`.

## Population Flow
`__populate_fs()`:
- Changes into the source directory, scans entries alphabetically, and recursively creates target entries.
- Preserves hardlinks by tracking `(src_dev, src_ino) -> dst_ino`.
- Handles regular files, directories, symlinks, devices, FIFOs, sockets, and ignores unknown types.
- Copies inode metadata and xattrs after creation.
- Supports callbacks before and after inode creation.

`populate_fs3()`:
- Requires a writable filesystem.
- Initializes hardlink/path tracking and link insertion mode.
- Treats `"-"` or a regular source file as a tar archive through `__populate_fs_from_tar()`.
- Otherwise copies xattrs on the root and recursively populates from a directory.
- `populate_fs2()` and `populate_fs()` are compatibility wrappers.

## Integration
Declared by `create_inode.h`; used by mke2fs image population. Also cooperates with `create_inode_libarchive` for tar input.

## Risks / Notes
- The recursive walker changes process working directory.
- Hardlink tracking lifetime is scoped to a single population run.
- `COPY_FLAGS_MASK` deliberately limits which host flags are copied.
- Path strings are grown manually through `path_append()`.
