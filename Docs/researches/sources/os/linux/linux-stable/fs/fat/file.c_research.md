# File Research: sources/os/linux/linux-stable/fs/fat/file.c

This file implements regular-file VFS operations and generic FAT ioctls.

Key responsibilities:
- Handle FAT attribute ioctls, volume ID query, and `FITRIM`.
- Define regular file operations and inode operations.
- Implement file release flushing, fsync, fallocate, truncate, getattr, and setattr.
- Enforce FAT mode and timestamp semantics.

Important functions:
- `fat_generic_ioctl()` dispatches `FAT_IOCTL_GET_ATTRIBUTES`, `FAT_IOCTL_SET_ATTRIBUTES`, `FAT_IOCTL_GET_VOLUME_ID`, and `FITRIM`.
- `fat_ioctl_set_attributes()` validates immutable/system behavior, maps DOS attributes to Unix mode changes, calls security hooks and `fat_setattr()`, updates immutable flags, saves attributes, and dirties the inode.
- `fat_file_release()` performs extra flushing when the `flush` mount option is enabled.
- `fat_file_fsync()` syncs file metadata buffers, FAT metadata buffers, and flushes the block device.
- `fat_fallocate()` supports preallocation with optional `FALLOC_FL_KEEP_SIZE`; unsupported flags and directories return `-EOPNOTSUPP`.
- `fat_free()` truncates cluster chains, updates EOF in FAT when keeping a prefix, invalidates cluster cache, and frees the remaining chain.
- `fat_truncate_blocks()` adjusts `mmu_private`, frees clusters past the requested offset, and flushes if configured.
- `fat_getattr()` fills stat data, exposes cluster size, maps NFS no-stale inode numbers to `i_pos`, and reports VFAT birth time.
- `fat_setattr()` handles permission checks, quiet-mode compatibility, size expansion before truncate, size shrinking with block tail zeroing, FAT timestamp truncation, and final inode dirtying.

Operations:
- `fat_file_operations` wires generic read/write/mmap/splice operations to FAT-specific ioctl, fsync, release, and fallocate.
- `fat_file_inode_operations` wires setattr/getattr/update_time.

Failure behavior:
- Attribute changes reject illegal `ATTR_VOLUME`/`ATTR_DIR` mutations, root attribute changes, and unauthorized system immutable changes.
- FAT mode sanitization quietly drops invalid chmod requests in historical compatibility cases.
- Truncate and fallocate paths are careful to avoid holes inconsistent with FAT allocation.

Research relevance:
- This is the regular-file policy layer above block mapping and FAT allocation. It translates Linux file operations into FAT’s no-holes, attribute-byte, coarse-timestamp model.
