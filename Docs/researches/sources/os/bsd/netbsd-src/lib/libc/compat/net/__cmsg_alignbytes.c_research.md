# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/net/__cmsg_alignbytes.c

Read completely: 68 lines.

This implements `__cmsg_alignbytes`, returning the alignment mask used for old control-message layout. It caches the value in a static local, tries to query `HW_ALIGNBYTES` via `sysctl` when available, and falls back to compile-time `ALIGNBYTES`.

Important interactions: consumed by compatibility socket ancillary-data macros/functions that must reproduce older alignment rules.

Security/reliability notes: the static cache is simple and unsynchronized, but races only compute the same small integer. Sysctl failure falls back safely.
