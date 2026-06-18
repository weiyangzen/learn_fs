# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/bzero.S

This ARM assembly file implements `bzero` by setting the fill byte to zero and branching into `_memset`. It conditionally declares a weak alias from `bzero` to `_bzero`.
