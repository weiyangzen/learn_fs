# File Research: sources/virtualization/libguestfs/daemon/utimens.c

## Role
Implements timestamp updates for guest filesystem paths.

## Main Operation
- `do_utimens()` maps sentinel nanosecond values `-1` to `UTIME_NOW` and `-2` to `UTIME_OMIT`.
- Calls `utimensat()` inside the guest chroot with `AT_SYMLINK_NOFOLLOW`.

## Semantics
The operation updates the path itself without following symlinks.

## Filesystem/Storage Relevance
This file mutates file atime and mtime metadata in guest filesystems.
