# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/statvfs.h

## Role

Defines the modern filesystem statistics ABI for `statvfs(2)` and `fstatvfs(2)`.

## Key Contents

Defines `_FSTYPSZ`/`FSTYPSZ`, `statvfs_t`, 32-bit `statvfs32_t`, large-file `statvfs64_t`, and 32-bit large-file `statvfs64_32_t`. Structures report block sizes, block counts, file counts, filesystem ID, base type, mount flags, maximum filename length, and filesystem-specific string.

Defines mount flags `ST_RDONLY`, `ST_NOSUID`, and `ST_NOTRUNC`.

## Interfaces

Handles `_FILE_OFFSET_BITS=64` and LP64 large-file remapping, then declares `statvfs`, `fstatvfs`, and transitional `statvfs64`/`fstatvfs64` where enabled.

## Design Notes

Like `stat.h`, this file is ABI-sensitive and preserves data-model-specific layout, including packed 32-bit large-file structures when required by alignment rules.
