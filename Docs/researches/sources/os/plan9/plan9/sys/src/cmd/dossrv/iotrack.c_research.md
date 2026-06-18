# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/iotrack.c

Sector cache for `dossrv`.

Key behavior:
- Caches tracks of 9 sectors (`Sect2trk`) in an 80-entry LRU, with a 31-bucket hash table.
- `getsect()` returns a read-filled sector; `getosect()` returns a sector for overwrite without forcing a read; both route through `getiosect()`.
- Tracks carry dirty, immediate-write, and stale flags; individual `Iosect` objects lock sectors within tracks.
- `getiotrack()` finds cached tracks or evicts an unreferenced LRU track, writing dirty data first.
- `tread()` and `twrite()` read/write complete tracks via `devread()`/`devwrite()`.
- `purgebuf()` flushes and invalidates all tracks for a backing `Xfs`.
- `sync()` flushes all dirty tracks.
- `iotrack_init()` initializes hash/LRU lists and allocates track buffers with `sbrk()`.

Filesystem relevance:
- Provides write-back sector buffering for FAT metadata and file data, including stale partial-track handling before writes.
