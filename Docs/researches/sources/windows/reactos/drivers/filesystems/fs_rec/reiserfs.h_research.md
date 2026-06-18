# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/reiserfs.h

This header defines the packed ReiserFS superblock subset used by `reiserfs.c`. It includes journal parameters, block counters, root block, block size, object-id metadata, mount state, magic string, filesystem state, hash function, tree height, bitmap count, version, and reserved journal size.

It uses `pshpack1.h`/`poppack.h` to enforce on-disk packing and has `C_ASSERT` checks for the expected offsets of `s_blocksize` and `s_magic`.

Constants:
- `REISERFS_DISK_OFFSET_IN_BYTES`: 64 KiB.
- Magic strings: `ReIsErFs`, `ReIsEr2Fs`, `ReIsEr3Fs`.
- `MAGIC_KEY_LENGTH`: 9.

Research notes:
- Header comment metadata says Btrfs, but the structure and constants are ReiserFS.
- Only `REISER2FS_SUPER_MAGIC_STRING` is currently used by the recognizer.
- This is a recognizer-only structure, not a complete ReiserFS format definition.
