# File Research: sources/os/linux/linux-stable/fs/quota/quota_v1.c

## Purpose
Implements support for the old VFS quota file format `QFMT_VFS_OLD`.

## Format
The quota file is a flat array of `struct v1_disk_dqblk`, indexed directly by uid/gid. Disk space limits are stored in 1 KiB quota blocks. Inode counts and limits are 32-bit fields. Grace times are stored in the record for ID 0.

## Main Functions
- `v1_disk2mem_dqblk()` and `v1_mem2disk_dqblk()`: convert between disk and in-memory quota structures.
- `v1_read_dqblk()`: reads a quota record by computed offset and marks all-zero limits as fake.
- `v1_commit_dqblk()`: writes a quota record, special-casing root user/group records to store grace times.
- `v1_check_quota_file()`: validates old-format layout and rejects files that appear to contain newer v2 magic.
- `v1_read_file_info()` / `v1_write_file_info()`: load and store global grace times and max limit metadata.

## Registration
Defines `v1_format_ops` and registers `v1_quota_format` at module init.

## Notes
This format supports user and group quotas only in its v2-magic rejection table and uses legacy fixed indexing, which makes sparse high IDs expensive/impractical compared with quota v2 trees.
