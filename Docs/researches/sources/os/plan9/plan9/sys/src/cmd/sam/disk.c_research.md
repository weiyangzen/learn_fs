# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/disk.c

Read status: complete, 118 lines.

`disk.c` manages the temporary disk file used by `sam` buffers. `diskinit` creates an ORCLOSE/OCEXEC temp file under `/tmp` with a pid/user-derived name.

Blocks are allocated in size buckets rounded by `Blockincr`. `disknewblock` reuses bucket free lists or allocates new block descriptors in chunks. `diskrelease` returns blocks to free lists. `diskwrite` may reallocate a block if its rounded size class changes, then writes runes with `pwrite`; `diskread` reads runes with `pread`.

Filesystem relevance: direct temp-file-backed storage allocator for editor buffers and undo logs.
