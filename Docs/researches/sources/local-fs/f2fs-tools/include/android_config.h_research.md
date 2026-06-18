# File Research: sources/local-fs/f2fs-tools/include/android_config.h

Provides a static configure-style capability header for Android/non-autoconf builds.

Key contents:
- For Linux, defines availability of common headers and functions: fcntl, fallocate, linux fs/ioctl/xattr/verity/fiemap headers, mount APIs, xattr APIs, uuid, clock APIs, sparse library, liblz4, libuuid, etc.
- Enables `HAVE_LIBSELINUX` only when `WITH_SLOAD` is defined.
- Enables `HAVE_LINUX_BLKZONED_H` for Bionic builds.
- For Apple, defines a smaller capability set including POSIX ACL, sys/mount, sys/xattr, fallocate, sparse, liblz4, and conditional libselinux.
- For Windows, only defines sparse support.

Role in the tree:
- Included by `f2fs_fs.h` under `WITH_ANDROID` when no generated `config.h` is present.
- Controls compile-time feature gates in mkfs, sload, xattr, device, and zoned support code.
