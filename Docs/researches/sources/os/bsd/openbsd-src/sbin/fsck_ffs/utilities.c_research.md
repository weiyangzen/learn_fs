# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/utilities.c

## Scope

Shared `fsck_ffs` utility layer: prompts, inode state lookup, block/cylinder-group buffer caches, raw I/O, finalization, allocation/free helpers, pathname reconstruction, signal handlers, progress reporting, and memory wrappers.

## Main APIs

- Prompt/state: `reply()`, `dofix()`, `ftypeok()`, `inoinfo()`.
- Buffer and I/O: `bufinit()`, `cglookup()`, `getdatablk()`, `getblk()`, `flush()`, `bread()`, `bwrite()`, `ckfini()`.
- Allocation/path helpers: `allocblk()`, `freeblk()`, `getpathname()`.
- Signals/progress: `catch()`, `catchquit()`, `voidquit()`, `catchinfo()`.
- Memory wrappers: `Malloc()`, `Calloc()`, `Reallocarray()`.

## Control Flow

The buffer cache is a small LRU of filesystem block buffers plus a lazily allocated cylinder-group cache. `getblk()` flushes dirty contents before reading a new block, while `flush()` writes dirty data and, for the primary superblock buffer, also writes summary info. `bread()` and `bwrite()` fall back to sector-by-sector diagnostics after whole-buffer I/O fails.

`ckfini()` blocks SIGINT, writes pending buffers, optionally updates the standard superblock, frees caches, marks the filesystem clean if requested and approved, prints cache stats in debug mode, closes descriptors, and restores the signal mask.

`allocblk()` scans for free fragments, updates `blockmap` and cylinder-group free maps/counters, and returns the allocated fragment. `freeblk()` delegates to `pass4check()`. `getpathname()` recursively follows `..` and directory names to build a path for diagnostics.

## Dependencies

- Uses globals from `main.c` and state from `setup.c`.
- Calls directory search callbacks `findino()` and `findname()` through `ckinode()`.
- Uses OpenBSD `SIGINFO` and `_PATH_TTY` for progress reporting.

## Risks And Edge Cases

- `ckfini()` is called from a signal handler path with an explicit comment noting a race.
- `reply()` sets `resolved = 0` on negative answers and read-only/no-write default denials.
- Cylinder-group cache memory wrappers try to reclaim cache entries before failing allocation.
- Raw I/O offsets are computed in `DEV_BSIZE` units, while fallback sector diagnostics use actual `secsize`.
