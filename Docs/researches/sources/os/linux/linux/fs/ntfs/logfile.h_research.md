# File Research: sources/os/linux/linux/fs/ntfs/logfile.h

This header defines the on-disk `$LogFile` restart structures and declares journal validation/emptying functions.

Constants:
- `MaxLogFileSize`: maximum supported LogFile size.
- `DefaultLogPageSize`: default 4096-byte log page size.
- `MinLogRecordPages`: minimum required log record pages after the restart pages.
- `LOGFILE_NO_CLIENT`: sentinel for no log client record.

Structures:
- `struct restart_page_header` describes the `RSTR`/`CHKD` restart page header, including USA metadata, system/log page sizes, restart area offset, and LogFile version fields.
- `struct restart_area` stores current LSN, log client list heads, clean-volume flags, sequence-number bit count, restart area/client array sizes, usable log file size, log record header/data offsets, and restart open count.
- `struct log_client_record` stores per-client oldest/restart LSNs, linked-list indexes, sequence number, and client name. For NTFS, the expected client is `"NTFS"`.

Flags:
- `RESTART_VOLUME_IS_CLEAN` marks clean shutdown state in newer Windows behavior.
- `RESTART_SPACE_FILLER` is a width filler.

Exported functions:
- `ntfs_check_logfile()` validates the journal and can return the current restart page.
- `ntfs_empty_logfile()` fills the journal with empty bytes after it has been deemed clean.

Role in subsystem:
This header provides the exact disk layout consumed by `logfile.c` and imported through `layout.h` magic/MST definitions. It is mount-time metadata infrastructure rather than general file I/O.
