# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_quotactl.S

Defines SPARC64 compatibility `quotactl`.

It warns callers to include `<sys/quota.h>` and maps to `compat_50_quotactl`.

This preserves old filesystem quota ABI.
