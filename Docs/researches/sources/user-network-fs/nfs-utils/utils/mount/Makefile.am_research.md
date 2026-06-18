# sources/user-network-fs/nfs-utils/utils/mount/Makefile.am

Purpose: automake recipe for the NFS mount/umount helper and associated man pages/config files.

Important build APIs: `sbin_PROGRAMS = mount.nfs`; `mount_common` collects shared mount sources, option parsers, protocol code, headers, and utilities. `MOUNT_CONFIG` adds `configfile.c` and the `nfsmount.conf` man page. `CONFIG_LIBMOUNT` switches between `mount_libmount.c` and legacy `mount.c`, `fstab.c`, and `nfsumount.c`.

Control flow: install hook creates symlinks `mount.nfs4`, `umount.nfs`, and `umount.nfs4`, and sets setuid permissions on `mount.nfs`. Uninstall removes symlinks. Man hooks remove generated link names.

State and persistence: affects installed helper names, permissions, and manual/config distribution files.

Dependencies and integration: links nfs-utils support libraries, export/reexport/misc libraries, libtirpc, pthread, and optionally libmount.

Risks: setuid install behavior is security-sensitive and packaging may override it. Build variants produce materially different mtab/utab code paths. Test signals include both `CONFIG_LIBMOUNT` paths, `MOUNT_CONFIG` on/off, install symlink layout, and helper invocation through all four names.
