# sources/user-network-fs/libfuse/include/fuse_mount_compat.h

`fuse_mount_compat.h` provides portability shims for mount and unmount flag macros on non-BSD platforms whose libc headers may lack Linux `MS_*` or `UMOUNT_*` definitions.

It exports no functions or types. It conditionally includes `<sys/mount.h>` and defines missing `MS_DIRSYNC`, `MS_NOSYMFOLLOW`, `MS_REC`, `MS_PRIVATE`, `MS_LAZYTIME`, `UMOUNT_DETACH`, `UMOUNT_NOFOLLOW`, and `UMOUNT_UNUSED`. Preprocessor guards skip the compatibility block on NetBSD, FreeBSD, DragonFly, and GNU/kFreeBSD.

There is no runtime state. The constants influence mount namespace behavior such as recursive/private propagation, lazy timestamp updates, symlink-follow policy, and detached unmounts. It is an internal integration aid for mount helper code and is not installed by `include/meson.build`.

Risks are incorrect Linux UAPI values, redefining incompatible BSD constants, or choosing a used bit for `UMOUNT_UNUSED`. Test signals include build coverage on glibc, musl-like libc variants, and BSD targets, plus runtime mount/unmount behavior checks for supported Linux flags.
