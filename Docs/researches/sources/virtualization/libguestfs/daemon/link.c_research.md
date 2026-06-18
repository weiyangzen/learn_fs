# File Research: sources/virtualization/libguestfs/daemon/link.c

Implements readlink-list and link creation APIs.

Important behavior:
- `do_internal_readlinklist` opens a directory fd under chroot and uses `fstatat`/`readlinkat` for each name.
- Missing/non-symlink/error entries intentionally return empty strings.
- `do_ln` and `do_ln_f` use hard-link syscalls under chroot.
- Symlink creation uses external `ln -s`/`ln -sf` with `--` so targets beginning with `-` are not parsed as options; linkname is sysroot-prefixed.

Filesystem relevance: link metadata and hard/symbolic link creation within guest filesystems.
