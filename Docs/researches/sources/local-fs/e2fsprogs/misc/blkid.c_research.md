# File Research: sources/local-fs/e2fsprogs/misc/blkid.c

## Purpose
Implements the `blkid` CLI over `libblkid`.

## Main Behavior
- Loads a blkid cache with optional read/write cache paths.
- Can garbage-collect the cache.
- Probes all devices, probes specified devices, or looks up the first matching token.
- Filters output by requested tags.
- Supports output formats: full `NAME="value"` records, value-only, device-only, and pretty list.

## Output Helpers
- `safe_print()` escapes non-printable bytes and double quotes.
- Pretty list mode gathers device name, filesystem type, label, UUID, and mount status via `ext2fs_check_mount_point()`.
- Terminal width is detected via ioctl or `COLUMNS`.

## Integration
Uses `blkid_get_cache`, `blkid_probe_all`, `blkid_verify`, `blkid_get_dev`, `blkid_find_dev_with_tag`, and tag iteration APIs.

## Risks / Notes
Device/tag arrays are fixed at 128 entries; too many `-s` tags is detected, but device overflow is not explicitly guarded.
