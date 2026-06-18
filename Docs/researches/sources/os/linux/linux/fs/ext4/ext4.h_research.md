# File Research: sources/os/linux/linux/fs/ext4/ext4.h

## Purpose

`ext4.h` is the central internal ext4 header. It defines ext4’s core on-disk formats, in-memory inode/superblock state, feature flags, mount flags, block mapping contracts, directory formats, allocation state, journaling hooks, and cross-file function declarations used throughout `fs/ext4`.

## Main Definitions

- Basic ext4 scalar types:
  - `ext4_grpblk_t`: block offset within a block group.
  - `ext4_fsblk_t`: filesystem-wide physical block number.
  - `ext4_lblk_t`: file logical block number.
  - `ext4_group_t`: block group number.

- Allocation and mapping:
  - `enum criteria` defines mballoc search levels, from fast power-of-two/goal searches to slow full group scans.
  - `EXT4_MB_HINT_*` flags describe allocator hints such as goal-only, delayed allocation reservation, stream allocation, reserved pool use, and strict checks.
  - `struct ext4_allocation_request` carries logical range, physical hints, neighboring blocks, requested length, target inode, and flags.
  - `struct ext4_map_blocks` is the compact mapping request/result object used by `ext4_map_blocks()` and related functions.
  - `EXT4_MAP_*` flags encode mapped, new, unwritten, delayed, boundary, and query-state results.

- On-disk metadata:
  - `struct ext4_group_desc` defines group descriptor layout, including block/inode bitmap locations, inode table location, free counts, checksum fields, exclude bitmap fields, and high 64-bit block address halves.
  - `struct ext4_inode` defines the on-disk inode, including classic fields, block array, OS-dependent fields, extended timestamps, checksum fields, creation time, version high bits, and project ID.
  - `struct ext4_super_block` defines the full ext4 superblock layout, including counts, block geometry, feature flags, journal references, hash seeds, 64-bit counters, MMP fields, quota inode numbers, checksum seed, encoding fields, orphan file inode, and final checksum.

- In-memory metadata:
  - `struct ext4_inode_info` wraps VFS inode state with ext4-specific fields:
    - raw block data, file ACL, block group, inode flags/state, xattr lock, orphan tracking, fast commit state, raw inode lock, disk size, data semaphore, JBD2 inode, metadata buffer tracking, creation time, preallocation state, extent status tree, pending cluster reservations, inline data fields, quota state, completed I/O lists, fsync transaction IDs, checksum seed, project ID, and fscrypt state.
  - `struct ext4_sb_info` is the large per-mounted-filesystem state object:
    - block geometry, descriptor arrays, mount options, reserved blocks, counters, block group locks, journal state, orphan info, quota config, buddy allocator state, mballoc tunables/statistics, locality groups, flex groups, writeback workqueues, MMP state, folio order limits, checksum seed, extent status shrinker, xattr caches, ratelimits, dummy encryption policy, writepages lock, DAX info, block device error tracking, fast commit queues/state, and atomic write unit limits.

## Feature and Flag Model

- Inode flags include ext2/ext3-compatible flags plus ext4 additions:
  - extents, huge file, verity, EA inode, DAX, inline data, project inheritance, casefolding, encryption, journal data, immutable, append-only, noatime, nodump.
- `ext4_check_flag_values()` uses build-time checks to keep `EXT4_*_FL` values aligned with `EXT4_INODE_*` bit numbers.
- Feature flags are split into:
  - compatible: journal, xattr, dir index, fast commit, stable inodes, orphan file.
  - readonly-compatible: sparse super, large file, huge file, metadata checksum, quota, bigalloc, project quota, verity, orphan present.
  - incompatible: compression, filetype, journal recovery, extents, 64bit, MMP, flex_bg, EA inode, inline data, encrypt, casefold, largedir, checksum seed.
- Macro-generated helpers provide `ext4_has_feature_*`, `ext4_set_feature_*`, and `ext4_clear_feature_*`.
- Supported feature masks define what this kernel can mount as ext2, ext3, or ext4.

## Directory and Name Handling

- Defines classic and modern directory entries:
  - `struct ext4_dir_entry`
  - `struct ext4_dir_entry_2`
  - `struct ext4_dir_entry_hash`
  - `struct ext4_dir_entry_tail`
- Casefolded encrypted directories store hashes after the aligned filename area.
- `ext4_dir_rec_len()` accounts for hash trailer space when needed.
- Directory record length conversion helpers handle special encodings for 64 KiB and larger block sizes.
- HTree directory constants and hash versions are declared, including legacy, half-MD4, TEA, unsigned variants, and SipHash.
- `struct ext4_filename` carries user name, disk name, hash info, optional fscrypt buffer, and optional casefold name.

## Journaling and Error Interfaces

- Declares ext4 journal trigger types and `struct ext4_journal_trigger`, currently including orphan-file checksum triggers.
- Error reporting interfaces include:
  - `__ext4_error`
  - `__ext4_error_inode`
  - `__ext4_error_file`
  - `__ext4_std_error`
  - `__ext4_warning`
  - `__ext4_msg`
  - `__ext4_grp_locked_error`
- Public macros add caller function and line metadata.
- Emergency state helpers return `-EIO` for forced shutdown and `-EROFS` for emergency read-only state.

## Allocation and Block Group State

- `struct ext4_group_info` tracks buddy allocator state for a block group:
  - free tree, first free block, total free blocks, fragments, largest/average free fragment order, prealloc list, optional double-check bitmap, allocation semaphore, and free counters by order.
- Group info bits track lazy initialization, trim state, corrupt block/inode bitmaps, and bitmap read state.
- Group lock helpers wrap per-blockgroup spinlocks and maintain a contention counter.
- Bigalloc macros convert between blocks and clusters and mask or fill cluster offsets.

## Inline Helpers and Invariants

- Timestamp helpers encode/decode extended epoch/nanosecond fields and gracefully handle old inode sizes where extra fields do not fit.
- Inode size helpers handle large directories and regular files using high size bits.
- Superblock count helpers read/write 64-bit block counters split into low/high fields.
- `ext4_valid_inum()` validates root inode and non-reserved inode ranges.
- `is_special_ino()` recognizes reserved, quota, and orphan-file inodes.
- `ext4_update_i_disksize()` and `ext4_update_inode_size()` serialize disk-size growth under `i_data_sem`.
- `ext4_inode_can_atomic_write()` allows atomic writes only for regular extent-based files with a nonzero filesystem atomic write unit minimum.

## Declared Cross-Module APIs

The header declares major ext4 subsystem entrypoints, including:

- bitmap checksum and validation
- block allocator and mballoc
- inode allocation, read/write, truncate, page write, DAX/iomap, project quota
- indirect block mapping
- extents mapping, insert, truncate, replay, fiemap, swap, unwritten conversion
- fast commit tracking, commit, replay cleanup
- directory indexing, lookup, insert, delete, inline directory handling
- resize and online group addition
- superblock read/checksum/error handling
- MMP
- orphan list/file handling
- fscrypt, fsverity, sysfs, read folio/readahead, page I/O

## Dependencies

- Linux kernel VFS, buffer-head, block-device, quota, fscrypt, fsverity, DAX, percpu counters, rbtrees, xarrays, shrinkers, JBD2.
- Includes `extents_status.h` and `fast_commit.h`, so inode and superblock structures directly embed extent status and fast commit state.

## Research Notes

This file is the architectural contract for ext4. Most implementation files depend on it for structure layout, flag compatibility, allocation constants, and subsystem prototypes. Changes here have wide blast radius because many definitions are both on-disk ABI and internal synchronization contracts.
