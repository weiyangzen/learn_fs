# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/stdlib/compat_random.c

Read completely: 66 lines.

This provides compatibility `initstate` and `srandom` wrappers whose seed type is `unsigned long`. Both cast the seed down to `unsigned int` and delegate to `__initstate60`/`__srandom60`.

Important interactions: preserves old symbol names via weak aliases and warnings.

Security/reliability notes: seed narrowing is intentional ABI compatibility. There is no cryptographic security claim for these PRNG APIs.
