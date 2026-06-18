# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/bloom.c

Purpose: Bloom filter for tracking scores present or absent in Venti arenas.

Key behavior:
- `bloominit` initializes size, default hash count, header parsing, bitmask, and data pointer.
- `readbloom` reads/parses the on-disk header and adjusts partition block size upward for large filter I/O.
- `resetbloom` allocates an empty in-memory filter.
- `loadbloom` reads the whole filter and counts set bits for stats.
- `writebloom` writes header plus filter data back to the partition.
- `gethashes` derives double-hash sequence values from SHA1 score bytes and reserves the header bit range.
- `_markbloomfilter` and `_inbloomfilter` perform bit setting/testing.
- Public `inbloomfilter` and `markbloomfilter` wrap access with locks and stats.
- `startbloomproc` launches a background writer thread.

Integration points:
- Uses pack/unpack helpers for Bloom headers, partition I/O, stats, locks, and Venti process/channel primitives.

Risks:
- `gethashes` casts score bytes to `u32int*`, so it assumes acceptable unaligned access for the target environment.
- `ignorebloom` bypasses filtering by making all lookups positive.
- Stats naming in `inbloomfilter` is non-obvious: a positive Bloom result increments `StatBloomMiss`, while a negative result increments `StatBloomHit`, likely reflecting avoided disk lookup semantics rather than membership semantics.
