# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_quotactl.S

Defines RISC-V compatibility `quotactl`.

It warns callers to include `<sys/quota.h>` and maps to `compat_50_quotactl`.

Filesystem relevance is direct through quota control.
