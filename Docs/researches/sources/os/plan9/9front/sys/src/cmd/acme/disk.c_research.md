# File Research: sources/os/plan9/9front/sys/src/cmd/acme/disk.c

This file implements Acme's temporary disk block allocator.

Key responsibilities:
- `tempfile()` creates a per-process temp file `/tmp/X<pid>.<user-prefix>acme` with `ORCLOSE|OCEXEC`.
- `diskinit()` allocates a `Disk` and opens the temp file, exiting if creation fails.
- `ntosize()` rounds a rune count up to the block allocation bucket size.
- `disknewblock()` allocates or reuses a `Block` from size-class free lists, assigning offsets in the temp file.
- `diskrelease()` returns a block to its size-class free list.
- `diskwrite()` rewrites a block, reallocating if the rounded size class changes.
- `diskread()` reads a block range fully with `pread`.

Important dependencies:
- Used by `Buffer` in `buff.c`.
- Uses `emalloc()`, `error()`, and Plan 9 pread/pwrite/create APIs.

Filesystem/storage relevance:
- This is the physical backing store for Acme's in-memory text model: text buffers and logs live in a temporary file with recyclable block metadata.

Notes:
- Blocks are allocated in chunks of 100 `Block` structs to reduce malloc overhead.
- It checks for temp-file address overflow when allocating new disk space.
