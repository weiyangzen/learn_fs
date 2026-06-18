# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_quotactl.S

Defines the m68k compatibility `quotactl` symbol. It warns that old references should include `<sys/quota.h>` to bind to the correct interface.

The wrapper maps `quotactl` to `compat_50_quotactl`, preserving the pre-NetBSD 5.0 quota-control ABI.

Filesystem relevance is direct: quota control is a filesystem administration syscall, and this file keeps old m68k quota tools ABI-compatible.
