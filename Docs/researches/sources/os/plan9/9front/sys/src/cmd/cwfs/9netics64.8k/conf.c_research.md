# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/9netics64.8k/conf.c

Build-specific runtime defaults for a 9netics 64-bit, 8K-block cwfs instance.

Important behavior:
- `main` starts at superblock 2.
- `localconfinit()` mirrors the 9netics32 pool/dump defaults.
- Protocol table exposes `serve9p2`; comment notes 64-bit fileservers cannot serve 9P1 correctly because `NAMELEN` is too large.
