# File Research: sources/os/linux/linux/fs/quota/quota_v1.c

Old VFS quota file format support. The v1 format stores a flat array of `struct v1_disk_dqblk` records indexed directly by numeric user/group ID.

Key responsibilities:
- Converts space units between bytes and 1 KiB quota blocks with `v1_stoqb()` / `v1_qbtos()`.
- Converts disk records to/from `struct mem_dqblk` using `v1_disk2mem_dqblk()` and `v1_mem2disk_dqblk()`.
- Reads a quota record at `v1_dqoff(id)` through `v1_read_dqblk()`.
- Writes a quota record through `v1_commit_dqblk()`.
- Detects old-format files and refuses files that appear to contain newer v2 magic via `v1_check_quota_file()`.
- Reads/writes global quota info from the root quota record with `v1_read_file_info()` and `v1_write_file_info()`.
- Registers the `QFMT_VFS_OLD` quota format at module init.

Important behavior:
- A zero-limit dquot is marked `DQ_FAKE_B`.
- Root user/group entries carry grace times in the v1 format.
- File info maximums are limited by 32-bit on-disk counters.
- Uses `dqio_sem` and `memalloc_nofs_save()` around quota IO.

Research notes:
- Supports user and group quota magics for v2 detection but is itself the legacy flat-array format.
- No project quota support is apparent in this old format file.
