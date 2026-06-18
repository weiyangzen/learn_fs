# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/dentry.c

Directory entry and file block addressing helpers, including direct/indirect block mapping, readahead, and truncation.

Key responsibilities:
- `getdir()` returns the `Dentry` slot within an `Iobuf`.
- `accessdir()` updates access/modification times, mutator uid, qid version, and marks buffers dirty for non-read-only devices.
- `preread()` queues readahead requests using `Rabuf` and `raheadq`.
- `rel2abs()` maps a relative file block number to an absolute disk block, allocating direct or indirect blocks if a tag is supplied.
- `dbufread()` implements simple sequential read-ahead strategy.
- `dnodebuf()` and `dnodebuf1()` fetch a file data/dir block by relative block number.
- `indfetch()` reads/allocates indirect block entries.
- `ibbpow()` and `ibbpowsum()` compute indirect fanout powers.
- `dtrunclen()` truncates to an arbitrary length, preserving and zeroing the partial final block.
- `dtrunc()` truncates a file to zero, freeing indirect and direct blocks in reverse order.

Important interactions:
- Uses `NDBLOCK`, `NIBLOCK`, `INDPERBUF`, `BUFSIZE`, and tags from `portdat.h`.
- Calls allocation/free helpers `bufalloc()` and `buffree()` from `sub.c`.
- Readahead is consumed by `rahead()` in `main.c`.

Research notes:
- `rel2abs()` supports variable indirect depth based on `NIBLOCK`; if exhausted it prints that one deeper level is not implemented.
- `dtrunclen()` uses `Truncstate` to free in forward order for partial truncations, while full truncation keeps historical reverse freeing.
- `trunczero()` currently calls `dnodebuf(..., Tfile, ...)`, so truncating can allocate the last block to zero-fill it.
