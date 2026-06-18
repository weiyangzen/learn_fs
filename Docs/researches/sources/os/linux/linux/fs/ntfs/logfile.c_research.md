# File Research: sources/os/linux/linux/fs/ntfs/logfile.c

This file validates and empties the NTFS `$LogFile` journal during mount/recovery-related handling. It checks restart pages and writes an empty journal pattern when the log is known clean.

Validation helpers:
- `ntfs_check_restart_page_header()` validates restart page magic context, system/log page sizes, restart page position, LogFile version 1.1, USA count/offset, restart area offset, and `chkdsk_lsn` usage.
- `ntfs_check_restart_area()` validates restart-area bounds, client array offset/alignment, list indexes, restart length, sequence-number bit calculation from file size, and log record header/data offsets.
- `ntfs_check_log_client_array()` walks free and in-use client lists, detects loops/overflow, and validates first-entry previous links.
- `ntfs_check_and_load_restart_page()` combines those checks, copies the full restart page, applies MST deprotection when needed, optionally checks active log clients, and returns the current LSN from either `RSTR` or `CHKD`.

`ntfs_check_logfile()`:
- Treats an already marked empty LogFile as clean.
- Bounds LogFile size to `MaxLogFileSize`, aligns it to the selected log page size, and verifies the minimum size of two restart pages plus `MinLogRecordPages`.
- Scans plausible page-aligned restart page locations rather than byte-scanning.
- Distinguishes empty pages, log record pages, restart pages, and chkdsk-modified restart pages.
- Loads up to two valid restart pages and chooses the one with the greater LSN.
- Returns the selected restart page to the caller when requested; caller must `kvfree()` it.
- Marks the volume LogFile-empty flag if the whole journal appears empty.

`ntfs_empty_logfile()`:
- Assumes prior consistency checking and clean journal state.
- Truncates LogFile page cache, maps the LogFile runlist, allocates a cluster-sized `0xff` buffer, and writes it over every mapped cluster in the initialized LogFile range.
- Handles unmapped runlist fragments by remapping and restarting from the relevant VCN.
- Uses block-device readahead and waits for the first writeback range to catch serious I/O errors.
- On success, truncates the page cache again and marks `NVolLogFileEmpty`.
- On runlist corruption or I/O failure, marks volume errors and returns false.

Role in subsystem:
The Linux NTFS driver does not replay arbitrary journal records here; it verifies restart-page consistency and can empty a clean journal. This protects mounts from dirty/unsupported LogFile states and avoids reprocessing an already emptied log.
