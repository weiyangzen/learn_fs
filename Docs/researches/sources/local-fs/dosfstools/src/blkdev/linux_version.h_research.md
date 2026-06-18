# File Research: sources/local-fs/dosfstools/src/blkdev/linux_version.h

Header for Linux kernel-version compatibility.

Contents:
- Includes `<linux/version.h>` when configured.
- Defines fallback `KERNEL_VERSION(a,b,c)` macro if unavailable.
- Declares `get_linux_version()`.

Role:
- Allows block-device code to compare kernel versions without depending unconditionally on Linux kernel headers.
