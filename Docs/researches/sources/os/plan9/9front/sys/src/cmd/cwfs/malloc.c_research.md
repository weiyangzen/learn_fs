# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/malloc.c

Purpose: Permanent allocation and iobuf pool setup for cwfs.

Key behavior:
- `memsize()` estimates available memory from `/dev/swap`, optionally scaled by `fsmempercent`; fallback is `16*MB`.
- `ialloc()` is a simple permanent allocator using `sbrk()`/`brk()`, with alignment adjustment and `mainmem` pool locking.
- `iobufinit()` computes the number of I/O buffers and hash buckets, rounds hash count upward to a prime, allocates `Hiob`, `Iobuf`, and raw block storage, then links buffers into per-hash circular LRU chains.
- `iobufmap()` and `iobufunmap()` expose or hide the raw backing pointer by toggling `Iobuf.iobuf`.

Notable details:
- `HWIDTH` targets eight buffers per hash bucket.
- The file deliberately allocates long-lived storage only; normal malloc/free lifecycle is avoided for server core structures.
