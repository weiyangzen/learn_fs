# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_quotactl.S

Defines SH3 compatibility `quotactl`.

It warns callers to include `<sys/quota.h>` and maps to `compat_50_quotactl`.

This preserves old filesystem quota-control ABI.
