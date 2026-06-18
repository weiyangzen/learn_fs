# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/save.c

## Purpose
`save.c` serializes an in-memory libblkid cache back to disk in the XML-like format parsed by `read.c`.

## Important APIs, Types, and Functions
The public API is `blkid_flush_cache()`. `save_dev()` writes one `<device>` record, including `DEVNO`, `TIME`, optional `PRI`, and all device tags.

## Control Flow
`blkid_flush_cache()` exits early for invalid caches, empty device lists, unchanged caches, unwritable targets, or non-regular temp-file fallbacks. For regular existing files it writes to `filename-XXXXXX`, emits all devices with a type, clears the changed flag on success, optionally links a `.old` backup, and renames the temp file over the cache.

## State, Persistence, Dependencies, Risks, and Test Signals
This is the persistence point for `blkid_cache`. Dependencies include list iteration, `mkstemp()`, `fdopen()`, `fchmod()`, `link()`, and `rename()`. Risks include unescaped tag values in the output format, direct-write fallback for special cache paths, unchecked `fchmod()` when `mkstemp()` fails, and backup-link behavior on unusual filesystems. Test signals include cache read/write round trips, changed-flag behavior, temp rename success, and no output for devices without `TYPE`.
