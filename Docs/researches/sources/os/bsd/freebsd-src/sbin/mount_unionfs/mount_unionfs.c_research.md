# File Research: sources/os/bsd/freebsd-src/sbin/mount_unionfs/mount_unionfs.c

## Summary
Mount helper for unionfs layered mounts.

## Main Responsibilities
- Parses `-b` deprecated below option and generic `-o` key/value options.
- Resolves uid/gid option values from names to numeric strings.
- Canonicalizes both source and union mount directory paths.
- Rejects overlapping paths where one is a subdirectory of the other.
- Builds `nmount()` iovecs for `fstype=unionfs`, `fspath`, `from`, and `errmsg`.

## Key Functions
- `subdir()`: checks path containment.
- `parse_uid()` / `parse_gid()`: resolve names or validate numeric IDs.

## Research Notes
The helper prevents recursive or self-covering union configurations by checking both path containment directions before mounting.
