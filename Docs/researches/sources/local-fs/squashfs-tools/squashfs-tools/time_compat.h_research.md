# File Research: sources/local-fs/squashfs-tools/squashfs-tools/time_compat.h

This small compatibility header abstracts timestamp setting for extracted unsquashfs output, especially symlinks.

Key function:
- `set_timestamp(char *pathname, struct inode *i)`: inline wrapper that sets both access and modification times to `i->time`.

Platform behavior:
- On OpenBSD, uses `utimensat(AT_FDCWD, pathname, times, AT_SYMLINK_NOFOLLOW)` with `struct timespec`.
- On other platforms, uses `lutimes(pathname, times)` with `struct timeval`.

Important detail:
- Both implementations avoid following symlinks, preserving symlink timestamps where supported.
- The header assumes `struct inode` has a `time` field and that the including file has suitable system headers/constants available.
