# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/Makefile

This makefile builds the illumos `zfs` command-line frontend.

Build targets and objects:
- Produces `zfs`.
- Compiles `zfs_main.o`, `zfs_iter.o`, and `zfs_project.o`.
- Builds message catalog fragments from the same source set and concatenates them into `zfs.po`.

Install behavior:
- Installs the real program under the standard command target from `Makefile.cmd`.
- Creates `/usr/sbin/zfs` as a symlink back to `/sbin/zfs`.
- Creates ZFS filesystem helper symlinks for `mount` and `umount` under both `/usr/lib/fs/zfs` and `/etc/fs/zfs`, all pointing back to `/sbin/zfs`. This matches `zfs_main.c`, where `argv[0]` selects normal `zfs` behavior or filesystem-specific mount/unmount behavior.

Dependencies:
- Links against ZFS and illumos support libraries: `libzfs_core`, `libzfs`, `libuutil`, `libumem`, `libnvpair`, `libsec`, `libidmap`, `libzutil`, and `libcmdutils`.
- `libcmdutils` is specifically noted for `list(9F)` functions used by project quota code.
- Includes common ZFS headers, kernel ZFS headers, and libzutil common headers.

Build configuration:
- Includes `Makefile.cmd`, `Makefile.cmd.64`, and `Makefile.ctf`.
- Uses GNU99 C mode.
- Defines `_REENTRANT`.
- Adds `DEBUG` for non-release builds.
- Enables parallel make with `.PARALLEL`.

Risk notes:
- The helper symlink layout is part of the runtime ABI for `/etc/fs/zfs/mount` and `/etc/fs/zfs/umount`; changing it affects legacy mount integration.
- Link library order matters because the frontend calls into libzfs, libzfs_core, libshare/idmap-facing code, nvlist helpers, and project quota support.
- The include paths intentionally mix userland and kernel ZFS headers; moving or narrowing them can break ioctl/property structure visibility.
