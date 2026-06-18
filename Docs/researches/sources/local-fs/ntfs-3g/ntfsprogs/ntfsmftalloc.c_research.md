# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsmftalloc.c

## Role

`ntfsmftalloc.c` implements `ntfsmftalloc`, a quarantined/developer utility that allocates and initializes a base or extent MFT record.

## Command-Line Contract

Usage is `ntfsmftalloc [options] device [base-mft-record]`.

Options include:

- `-n`: no-action/read-only mount.
- `-f`: force execution despite mount checks.
- `-q`, `-v`, `-vv`.
- `-V`: version.
- `-l`: license.
- `-h`: help.

If a base MFT record number is supplied, the allocated record is an extent linked to that base inode. Without it, a base MFT record is allocated.

## Control Flow

1. `parse_options()` prints the version banner, parses device and optional base MFT number.
2. `main()` checks whether the device is mounted and refuses unless forced.
3. It mounts read-only for `-n`, otherwise read-write.
4. It registers `ntfsmftalloc_exit()` with `atexit()` to close inodes and unmount on failure.
5. If a base MFT number was supplied, it opens the base inode.
6. It calls `ntfs_mft_record_alloc(vol, base_ni)`.
7. In very verbose mode, it dumps the allocated MFT record header.
8. It closes the allocated/base inode, unmounts, and disables the failure cleanup path by setting `success = TRUE`.

## Important Dependencies

The utility depends on ntfs-3g MFT allocation internals, inode open/close, volume mount/unmount, mount-state checks, and logging. It is built as a quarantined program in `Makefile.am`, not as a normal installed tool.

## Risk Areas

- This is a direct metadata allocator and should be treated as a developer/test tool.
- `-n` only changes the mount flags to read-only; the code still calls `ntfs_mft_record_alloc()`, relying on lower layers to prevent writes.
- The parser rejects base record `0` because it treats `!ll` as invalid.
- Failure cleanup mutates global `ni` to `base_ni` before close, which is intentional but makes ownership subtle.
