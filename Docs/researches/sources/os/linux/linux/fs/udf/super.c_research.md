# File Research: sources/os/linux/linux/fs/udf/super.c

Purpose: UDF filesystem registration, mount/remount, descriptor scanning, partition setup, LVID management, teardown, and statfs.

Key behavior:
- Registers the `udf` filesystem and creates the UDF inode slab cache.
- Implements `fs_context` option parsing for block size, session, last block, anchor, visibility flags, AD format, strictness, uid/gid handling, permission masks, and charset.
- `udf_check_vsd()` scans the Volume Structure Descriptor area for NSR02/NSR03, including special 4 KiB media handling.
- Anchor scanning tries user-provided anchor, block 256, last-block variants, last-256 variants, and block 512 for open media.
- `udf_process_sequence()` reads main/reserve volume descriptor sequences, follows bounded descriptor pointers, selects prevailing descriptors by sequence number, then loads PVD, LVD, and partition descriptors.
- `udf_load_logicalvol()` parses partition maps and configures type 1, virtual, sparable, and metadata partition map state.
- `udf_load_partdesc()` fills partition root/length/access/free-space info and later resolves VAT or metadata dependencies.
- `udf_load_metadata_files()` loads metadata, mirror, and optional metadata bitmap file entries.
- `udf_load_logicalvolint()` finds the prevailing Logical Volume Integrity Descriptor across bounded redirections.
- `udf_open_lvid()`, `udf_close_lvid()`, `udf_sync_fs()`, and `lvid_get_unique_id()` manage LVID state, implementation ID, consistency marker, CRC/checksum, dirty tracking, and unique ID allocation.
- `udf_fill_super()` ties mount together: allocates `udf_sb_info`, scans possible block sizes, validates UDF revisions, loads fileset/root inode, opens LVID for writable mounts, and installs root dentry.
- `udf_statfs()` reports block counts and approximates inode counts from LVID file/dir counts plus free blocks.
- Free-space counting uses LVID first, then unallocated bitmap, then unallocated table.

Integration:
- Central owner of `struct udf_sb_info`, partition maps, mount options, LVID buffer, NLS map, VAT inode, and root inode setup.
- Calls helpers from `misc.c`, `partition.c`, `unicode.c`, `udftime.c`, inode/directory allocation, and low-level CD/session helpers.
- Provides `udf_sb_ops` and filesystem type registration.

Risks and invariants:
- Read-write mounts are rejected or coerced when descriptors are write-protected, dirty, unsupported, VAT-backed, missing LVID, or above max write revision.
- Numerous corruption guards bound table lengths, partition overflow, LVID indirections, descriptor pointer nesting, sparing table count/size, and map table length.
- Error cleanup releases VAT inode, NLS map, LVID, partition maps, and superblock private info.
