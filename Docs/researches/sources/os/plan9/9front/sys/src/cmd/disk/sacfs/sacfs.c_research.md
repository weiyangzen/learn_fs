# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sacfs.c

## Purpose
Implements a read-only 9P server for SAC filesystem images.

## Key Behavior
- Loads the entire SAC image into memory, validates magic and length, records block size, initializes the root `SacDir`, and allocates a small decompressed-block cache.
- Can serve over stdio (`-i`), post a service file (`-s`), or mount at a mountpoint (`-m`, default `/n/c:`).
- Implements legacy 9P request handlers for attach, clone, walk, clwalk, open, read, clunk, stat, session, flush, and erroring write/create/remove/wstat as read-only.
- Maintains `Fid` objects with user, qid, open state, and a copy of the current `Sac` directory entry.
- Tracks parent paths with reference-counted `Path` nodes so `..` can reconstruct parent directory entries from stored directory blocks.
- `loadblock()` reads uncompressed blocks directly or decompresses negative-offset blocks with `unsac()`, caching decompressed results by image offset.
- `saclookup()` performs directory lookup, currently using a linear search over directory entries; a binary-search implementation remains disabled in unreachable code.
- `sacdirread()` converts directory entries into Plan 9 `Dir` records, with SAC directory length interpreted as number of entries.
- Permission checks are simple owner/group/other mode comparisons, assuming each group name corresponds directly to a user.

## Interfaces And Dependencies
- Uses legacy `<fcall.h>` message conversion and direct pipe/service-file mounting rather than the newer `9p` library.
- Uses `sacfs.h` on-disk structures and `unsac()` from `unsac.c`.

## Notes
The server is intentionally read-only and memory-resident. It trusts the image more than a hardened filesystem would: malformed offsets or directory metadata can lead to fatal errors during block load/decompression.
