# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/hash.c

Hash helpers for gefs block integrity and hash-table indexing.

Key responsibilities:
- Provides MetroHash64 implementation with fixed gefs seed.
- Hashes arbitrary buffers and whole gefs blocks.
- Provides `ihash()` integer finalizer for distributing ids across hash tables.

Important behavior:
- `bufhash()` and `blkhash()` use seed `0x6765`.
- MetroHash reads native unaligned integer widths through casts.

Notable risks:
- The native-width reads assume the target architecture tolerates the access pattern used here.
