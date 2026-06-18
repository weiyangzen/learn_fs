# File Research: sources/os/bsd/freebsd-src/sbin/mount_msdosfs/mount_msdosfs.c

## Summary
Mount helper for FAT/MS-DOS filesystems. It maps command-line options into msdosfs `nmount()` iovecs, including name handling, uid/gid/mode defaults, and charset conversion.

## Main Responsibilities
- Supports short names, long names, no Win95 mode, uid, gid, file mask, directory mask, generic options, locale, DOS codepage, and predefined conversion tables.
- Defaults uid, gid, and masks from the mountpoint when not explicitly set.
- Loads `msdosfs_iconv` and registers charset mappings when local or DOS charset options are provided.
- Builds iovecs for `fstype=msdosfs`, `fspath`, `from`, `errmsg`, `uid`, `gid`, `mask`, and `dirmask`.
- Calls `nmount()` and reports kernel error text.

## Key Functions
- `a_uid()`, `a_gid()`, `a_mask()`.
- `set_charset()`: registers Unicode/local and DOS/local conversion pairs.

## Research Notes
When only a DOS charset is specified, local charset defaults to `ISO8859-1`. File and directory masks default together unless one was explicitly supplied.
