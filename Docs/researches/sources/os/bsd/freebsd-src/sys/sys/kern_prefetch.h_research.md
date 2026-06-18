# File Research: sources/os/bsd/freebsd-src/sys/sys/kern_prefetch.h

Kernel-only prefetch helper. On amd64, `kern_prefetch()` emits a `prefetcht1` instruction against the supplied address while using the `before` pointer as an inline-assembly memory constraint.

Other architectures currently compile the helper to no operation, with a commented `__builtin_prefetch` placeholder.
