# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsdump_logfile.c

## Role

Implements `ntfsdump_logfile`, a diagnostic utility that reads NTFS `$LogFile` either from a mounted-by-tool volume or from a standalone file copy and dumps interpreted restart/log-record structures.

## Main Functions

- `logfile_open()` opens either an NTFS volume read-only and `$LogFile/$DATA`, or a raw file with `-f`.
- `logfile_pread()` abstracts positioned reads from the NTFS attribute or raw file.
- `restart_header_sanity()` validates restart-page magic, page sizes, version 1.1, update sequence array placement, and restart-area alignment.
- `dump_restart_areas_header()` and `dump_restart_areas_area()` print restart page and client-record fields.
- `dump_restart_areas()` MST-deprotects the two restart pages, skips the second if it matches the first, and aborts on CHKD/BAAD cases.
- `dump_log_record()` prints decoded fields from a single log record.
- `dump_log_records()` walks record pages after the restart pages and prints page and record fields using fixed offsets.
- `main()` caps input to 64 MiB, reads it into memory, validates initial magic, dumps restart pages, then dumps log pages.

## Dependencies

Uses libntfs-3g volume, inode, attribute, logfile layout structures, MST fixups, endian helpers, utilities, and logging.

## Important Behavior

The tool is read-only but aborts on many unsupported/corrupt log states. It treats all-`0xff` data as an uninitialized `$LogFile`. It warns when only the first 64 MiB is analyzed.

Several sanity checks are explicitly TODO: restart-area checking, log-client array checking, richer command-line parsing, and more complete log record handling.

## Research Notes

This is an inspection aid rather than a repair or replay implementation. The parser has hard-coded assumptions such as version 1.1 and a `0x40` log-record start offset.
