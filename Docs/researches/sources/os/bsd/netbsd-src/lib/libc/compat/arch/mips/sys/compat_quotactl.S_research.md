# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_quotactl.S

Defines MIPS compatibility `quotactl`.

It warns that `<sys/quota.h>` should be included and maps the public symbol to `compat_50_quotactl`.

Filesystem relevance is direct because `quotactl` manages filesystem quotas.
