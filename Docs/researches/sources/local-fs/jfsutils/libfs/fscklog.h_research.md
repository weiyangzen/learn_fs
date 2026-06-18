# File Research: sources/local-fs/jfsutils/libfs/fscklog.h

## Purpose
Defines the on-aggregate fsck service log and extracted-check-log record headers.

## Key Definitions
- `flog_eyecatcher_string`: `"fscklog "`.
- `JFSCHKLOG_FIRSTMSGNUM`: first service-log message number, 10000.
- `XCHKLOG_BUFSIZE`: 8192-byte block size for extracted log files.
- `jfs_chklog_eyecatcher`: `"JFS chkdskSvcLog"`.

## Data Structures
- `struct fscklog_entry_hdr`: 16-bit entry length for in-aggregate service log entries.
- `struct fscklog_error`: records failed log write offset, bytes written, and I/O return code.
- `struct chklog_entry_hdr`: 16-bit entry length for extracted check-log files.

## Dependencies
Includes `jfs_types.h` for integer types.

## Notes
`fsckwsp.h` stores `fscklog_error` records in the workspace block-map control page, and `jfs_endian.c` provides byte-swapping for `fscklog_entry_hdr`.
