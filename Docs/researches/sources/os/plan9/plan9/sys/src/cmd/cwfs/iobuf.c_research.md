# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/iobuf.c

Hash/LRU buffer cache for filesystem blocks.

Key responsibilities:
- `getbuf()` looks up an `(Device*, addr)` buffer in a hash bucket, moves hits to the front, locks and maps the buffer, and reads from device on misses if `Brd` is set.
- Miss replacement selects the oldest unlocked, non-reserved entry in the hash line.
- Dirty victims are synchronously written before reuse.
- `syncblock()` writes at most one dirty block per hash line and reports whether more work remains.
- `sync()` repeatedly calls `syncblock()` up to `10*nhiob` passes.
- `putbuf()` handles immediate writes (`Bimm`), unmaps, and unlocks.
- `checktag()` validates the block trailer tag and qpath, flushing invalid clean buffers from cache and warning on mismatch.
- `settag()` writes tag and qpath into the block trailer and marks modified.
- `iobufql()` diagnoses whether a `QLock` belongs to a cached buffer.

Important interactions:
- Uses `devread`/`devwrite` dispatch from `sub.c`.
- `Bres` prevents replacement of pseudo/reserved buffers that may recursively call buffer-cache code.
- `checktag()` calls `cwfree()` when a bad tag is found on a `Devcw` block.

Research notes:
- The hash function mixes block address with the `Device*` pointer.
- `getbuf()` loops until it can lock and map a stable matching buffer; this handles races where a buffer is reused between lookup and lock.
- `checktag()` returns `2` for tag mismatch, `0` for accepted path mismatches in one branch, and `0` for success, matching existing caller expectations rather than normal boolean style.
