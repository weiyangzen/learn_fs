# File Research: sources/os/linux/linux/fs/exfat/misc.c

## Purpose
Provides shared exFAT helpers for filesystem error policy, timestamp conversion, atime truncation, checksums, buffer-head dirty/sync handling, and simple chain initialization/copy.

## Main Interfaces
- `__exfat_fs_error`
- `exfat_get_entry_time`, `exfat_set_entry_time`
- `exfat_truncate_atime`, `exfat_truncate_inode_atime`
- `exfat_calc_chksum16`, `exfat_calc_chksum32`
- `exfat_update_bh`, `exfat_update_bhs`
- `exfat_chain_set`, `exfat_chain_dup`

## Key Data Flow
`__exfat_fs_error()` reports corruption/inconsistency and applies the mount `errors=` policy: continue, panic, or remount read-only. Timestamp conversion maps exFAT date/time/centisecond/timezone fields to `timespec64` and back. Access time is rounded down to exFAT’s two-second granularity.

Checksum helpers implement the exFAT rolling checksum variants, skipping specified fields for directory-entry and boot-sector checksum modes. Buffer helpers mark buffer heads uptodate/dirty and optionally synchronously write/wait for them.

## Dependencies
Used throughout dir, inode, super, FAT, bitmap, and file code. Depends on mount options in `exfat_sb_info`, buffer-head APIs, kernel time helpers, and raw checksum type constants.

## Notable Invariants And Risks
- Error policy can mutate the superblock into read-only state.
- `exfat_set_entry_time()` records UTC offset as valid zero offset.
- Directory-entry checksum skips the checksum field itself.
