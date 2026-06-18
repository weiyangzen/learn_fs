# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/read.c

## Purpose
`read.c` parses the libblkid cache file so callers can resolve known devices without rescanning every block device.

## Important APIs, Types, and Functions
The public entry point is `blkid_read_cache()`. Parsing helpers include `skip_over_blank()`, `skip_over_word()`, `strip_line()`, `parse_start()`, `parse_end()`, `parse_dev()`, `parse_token()`, `parse_tag()`, and `blkid_parse_line()`. A debug-only main dumps parsed devices.

## Control Flow
`blkid_read_cache()` opens the cache, skips reread if mtime is unchanged or in-memory data is dirty, reads lines including backslash continuations, and lets `blkid_parse_line()` build or update a `blkid_dev`. Device names are taken from `<device ...>name</device>`, and attributes such as `DEVNO`, `PRI`, `TIME`, `TYPE`, `LABEL`, and `UUID` are parsed from XML-like attributes.

## State, Persistence, Dependencies, Risks, and Test Signals
The file mutates `blkid_cache` device/tag lists and updates `bic_ftime` while clearing the changed flag after a clean read. It depends on `blkidP.h`, libuuid headers, libc file I/O, and `strtoull` or `strtoul`. Risks include a deliberately shallow XML parser, quote/backslash edge cases, fixed 4096-byte input buffers, and silently continuing after malformed lines. Test signals include the `TEST_PROGRAM`, cache files with comments/continuations, required `TYPE` validation, and round trips with `save.c`.
