# File Research: sources/os/linux/linux-stable/fs/ntfs/logfile.h

## Summary
Defines NTFS `$LogFile` restart-page, restart-area, and log-client on-disk structures plus the public LogFile validation/emptying API.

## Main Contents
- LogFile sizing constants: `MaxLogFileSize`, `DefaultLogPageSize`, and `MinLogRecordPages`.
- `struct restart_page_header` for `RSTR`/`CHKD` restart pages.
- `LOGFILE_NO_CLIENT` constants.
- restart-area flags including `RESTART_VOLUME_IS_CLEAN`.
- `struct restart_area`.
- `struct log_client_record`.
- Declarations for `ntfs_check_logfile()` and `ntfs_empty_logfile()`.

## Important Details
The comments document the circular LogFile layout, dual restart pages, version expectations, Windows clean/dirty interpretations, client list conventions, restart-area alignment rules, and the fixed NTFS log client name. The driver expects one log client and supports version 1.1 semantics.

## Risks
Many fields are interpreted only after bounds and update-sequence validation in `logfile.c`; direct consumers must not trust offsets, lengths, or client indices without those checks.
