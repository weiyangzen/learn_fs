# File Research: sources/local-fs/erofs-utils/lib/liberofs_private.h

This private header centralizes optional platform/private includes and a compatibility shim.

Conditional includes:
- SELinux headers when `HAVE_LIBSELINUX`.
- Android filesystem config and canned fsconfig headers when `WITH_ANDROID`.

Compatibility:
- Provides an inline `memrchr()` implementation when the platform lacks it. It scans backward through a byte range and returns the last matching byte pointer or `NULL`.

Private API:
- `int erofs_tmpfile(void);`

Known users:
- `inode.c` uses Android/SELinux-related configuration paths.
- `metabox.c` and `remotes/oci.c` use `erofs_tmpfile()` for temporary staging.
