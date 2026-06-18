# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucHashVal.cc

## Purpose
Implements the string hash function used by `XrdOucHash`.

## Important APIs, Types, And Functions
`XrdOucHashVal(const char*)` hashes a null-terminated string by delegating to `XrdOucHashVal2(const char*, int)`. `XrdOucHashVal2` returns the raw bytes for short keys up to `sizeof(unsigned long)` and otherwise XORs machine-word chunks seeded by key length, returning 1 instead of zero.

## Control Flow
For short names the function copies bytes into an `unsigned long`. For longer names it handles a leading remainder, then walks word-sized blocks via `memcpy` and XOR accumulation.

## State And Persistence
No state.

## Dependencies And Integration Points
Uses C string headers and is declared externally by `XrdOucHash.icc`. The hash result is bucketed by `XrdOucHash<T>`.

## Risks And Test Signals
Risks include architecture-dependent results due to word size and endian layout, weak collision resistance from XOR folding, and reliance on callers passing valid buffers of `KeyLen` bytes. Test signals include stable hash distribution for representative keys on supported architectures, zero-hash avoidance, and consistency between `XrdOucHashVal` and `XrdOucHashVal2(strlen)`.
