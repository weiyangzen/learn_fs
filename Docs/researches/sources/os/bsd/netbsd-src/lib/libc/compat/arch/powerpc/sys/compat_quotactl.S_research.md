# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_quotactl.S

Defines PowerPC compatibility `quotactl`.

It warns callers to include `<sys/quota.h>` and routes the symbol to `compat_50_quotactl`.

This is directly relevant to filesystem quota ABI compatibility.
