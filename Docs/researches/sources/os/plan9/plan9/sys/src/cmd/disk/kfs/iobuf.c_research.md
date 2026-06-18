# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/iobuf.c

This file implements the KFS buffer cache.

Key behavior:
- Maintains hash buckets of `Iobuf` entries through `Hiob.link` and per-bucket locks.
- `getbuf` looks up an active block by device/address, moves hits to the front of an LRU ring, locks the buffer, sets requested flags, and reads or initializes on misses.
- On eviction, dirty buffers are written through `devwrite`; reserved buffers are skipped.
- `syncblock` writes at most one dirty block per hash bucket and reports whether work remains.
- `sync` repeatedly calls `syncblock`.
- `putbuf` checks lock state, writes immediate buffers (`Bimm`) synchronously, deactivates `iobuf`, and unlocks.
- `checktag` validates block trailer tag and qid path.
- `settag` writes a block tag and marks the buffer dirty.

Dependencies:
- Device methods from `fns.h`.
- Global stats filters in `cons`.
- Block tag layout from `portdat.h`.

Notable details:
- `Bimm` forces writeback on `putbuf`; this is used for metadata that should become durable quickly.
- `checktag` tolerates an old qid-path bug where the stored path includes `QPDIR`.
