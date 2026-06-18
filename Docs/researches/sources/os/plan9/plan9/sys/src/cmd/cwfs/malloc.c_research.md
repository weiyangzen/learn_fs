# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/malloc.c

Permanent allocation and buffer-cache memory initialization.

Key responsibilities:
- `ialloc()` wraps `mallocalign`, panics on failure, and zeros memory.
- `prbanks()` prints fake memory bank ranges.
- Installs `memory` console command via `cmd_memory()`.
- `iobufinit()`:
  - Computes total configured memory from `mconf.bank`.
  - Derives number of `Iobuf`s and hash buckets.
  - Allocates `Hiob` hash headers, `Iobuf` array, and contiguous raw buffer storage.
  - Initializes per-buffer qlocks and circular LRU lists per hash bucket.
  - Marks memory as consumed and prints remaining memory.
- `iobufmap()` maps an `Iobuf` by assigning `xiobuf` to `iobuf`.
- `iobufunmap()` marks `iobuf` invalid with `(char*)-1`.

Research notes:
- `HWIDTH = 8` targets eight buffers per hash chain.
- `nhiob` is adjusted upward to a prime number.
- This user-mode version does not actually map/unmap physical memory; mapping is pointer assignment.
