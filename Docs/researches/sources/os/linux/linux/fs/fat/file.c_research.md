# File Research: sources/os/linux/linux/fs/fat/file.c

## Purpose
Implements regular-file operations, FAT ioctls, fsync, fallocate, truncation, getattr/setattr, and file attribute reporting.

## Main Responsibilities
- Handles FAT-specific ioctls for DOS attributes, volume id, and trim.
- Defines `fat_file_operations` and `fat_file_inode_operations`.
- Implements FAT fsync over file metadata, FAT metadata, and block-device flush.
- Supports preallocation through `fallocate`.
- Frees cluster chains on truncate.
- Translates VFS setattr/getattr into FAT semantics.

## Key Interfaces
- `fat_generic_ioctl()`: dispatches FAT attribute, volume id, and `FITRIM` commands.
- `fat_file_fsync()`: syncs file metadata buffers, FAT metadata buffers, then flushes block device.
- `fat_truncate_blocks()`: frees clusters after a target offset and adjusts `mmu_private`.
- `fat_fileattr_get()`: reports immutable and casefold/case-preserving flags.
- `fat_getattr()`: fills `kstat`, reports cluster block size, optional NFS `i_pos` ino, and VFAT birth time.
- `fat_setattr()`: applies mode/uid/gid/size/time changes under FAT restrictions.

## Important Behavior
`fat_ioctl_set_attributes()` masks off invalid bits, prevents changing volume/dir bits, applies the read-only attribute through chmod-like mode changes, enforces `sys_immutable`, calls LSM setattr checks, then updates FAT attributes.

`fat_fallocate()` supports only normal extension and `FALLOC_FL_KEEP_SIZE`. KEEP_SIZE allocates clusters without zeroing if the requested range exceeds current on-disk allocation; non-KEEP_SIZE delegates to expanding truncate via `fat_cont_expand()`.

`fat_free()` invalidates the cluster cache before chain changes, writes inode size/start-cluster changes first, writes EOF at the kept cluster if truncating partially, updates `i_blocks`, and frees the remaining chain.

`fat_setattr()` preserves old FAT behavior for quiet failures, rejects uid/gid changes away from mounted uid/gid, sanitizes modes to all-or-none writable semantics, zeroes partial truncate pages, and truncates FAT timestamps manually rather than relying on generic setattr copying.

## Dependencies
Uses cluster allocation/free from `fatent.c` and `misc.c`, mapping/truncation from `inode.c`, and attribute helpers from `fat.h`.

## Research Notes
FAT has no native Unix ownership/mode model, so this file enforces mount-option-derived invariants instead of direct metadata persistence. `mmu_private` is central to avoiding writes into unallocated holes.
