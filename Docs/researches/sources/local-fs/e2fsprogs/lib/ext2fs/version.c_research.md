# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/version.c

## Purpose
Exposes libext2fs version and release date.

## Main Behavior
- Uses `E2FSPROGS_VERSION` and `E2FSPROGS_DATE` from `../../version.h`.
- `ext2fs_parse_version_string()` parses digits and at most one dot into a compact integer form, stopping at non-version characters.
- `ext2fs_get_library_version()` optionally returns version/date strings and returns the parsed version number.

## Integration
Used by tools or callers needing the runtime library version.

## Risks / Notes
The parser intentionally ignores suffixes after the numeric major/minor portion.
