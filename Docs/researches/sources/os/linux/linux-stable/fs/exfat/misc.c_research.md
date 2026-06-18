# File Research: sources/os/linux/linux-stable/fs/exfat/misc.c

This file contains shared utility routines for filesystem error handling, timestamp conversion, checksum computation, buffer-head update/sync, and simple chain initialization.

Key elements:
- `__exfat_fs_error()` reports corruption/inconsistency and applies the mount `errors=` policy: continue, panic, or remount read-only.
- Timestamp helpers convert between exFAT date/time fields and Unix `timespec64`.
- Timezone handling uses either recorded exFAT timezone offsets, system timezone mode, or mount `time_offset`.
- `exfat_truncate_atime()` and `exfat_truncate_inode_atime()` enforce exFAT access-time granularity.
- `exfat_calc_chksum16()` computes directory-entry checksums, skipping primary checksum bytes when requested.
- `exfat_calc_chksum32()` computes boot/upcase checksums, skipping boot-sector mutable fields for boot checksum mode.
- `exfat_update_bh()` marks one buffer uptodate/dirty and optionally synchronously writes it.
- `exfat_update_bhs()` marks and optionally synchronously writes multiple buffers, waiting and returning `-EIO` if any sync write fails.
- `exfat_chain_set()` and `exfat_chain_dup()` initialize/copy `struct exfat_chain`.

Important dependencies:
- Directory, inode, FAT, bitmap, and name code all call these helpers.
- Error handling is used to escalate metadata corruption consistently.
- Timestamp helpers are used in inode writeback, lookup, create, mkdir, setattr, and volume metadata paths.

Failure/edge behavior:
- `EXFAT_ERRORS_RO` mutates `sb->s_flags` to read-only when corruption is reported.
- `exfat_set_entry_time()` writes timezone-valid with zero offset, effectively storing UTC-equivalent timestamps.
