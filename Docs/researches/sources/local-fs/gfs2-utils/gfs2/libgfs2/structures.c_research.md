# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/structures.c

This file builds core GFS2 filesystem structures for mkfs-style creation and journal initialization.

Public APIs:
- `lgfs2_build_master()`, `lgfs2_build_root()`
- `lgfs2_sb_write()`
- `lgfs2_log_header_hash()`, `lgfs2_log_header_crc()`
- `lgfs2_write_journal_data()`, `lgfs2_write_journal()`, `lgfs2_build_journal()`
- `lgfs2_build_jindex()`
- `lgfs2_build_inum_range()`, `lgfs2_build_statfs_change()`, `lgfs2_build_quota_change()`
- `lgfs2_build_inum()`, `lgfs2_build_statfs()`, `lgfs2_build_rindex()`, `lgfs2_build_quota()`
- `lgfs2_init_inum()`, `lgfs2_init_statfs()`
- `lgfs2_check_meta()`
- `lgfs2_bm_scan()`

Behavior:
- Creates master and root directories as dinodes.
- Writes superblock at the fixed basic-block address while zeroing preceding blocks.
- Initializes journals with log headers, hashes, CRCs, sequence numbers, physical addresses, and unmount/userspace flags.
- Builds system files/directories: jindex, inum, statfs, rindex, quota, per-node inum/statfs/quota change files.
- Writes rindex entries from the resource-group tree plus an extra zero entry without resizing.
- Scans bitmaps for matching state.

Integration role:
- Heavily used by `mkfs.gfs2` and related structure setup.
- Depends on CRC-32C, disk hash, inode creation, file writes, block mapping, and ondisk conversion.

Risk notes:
- Journal creation has two paths: through mapped file buffers and through direct contiguous writes.
- `lgfs2_write_filemeta()` assumes single-extent allocation created by `lgfs2_file_alloc()`.
- Superblock write uses `pwritev()` and expects full write.
- Incorrect journal hash/CRC or physical address calculation makes recovery fail.
