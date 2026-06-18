# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/iotrack.c

## Purpose
Implements a track-oriented sector cache for `dossrv`.

## Key Behavior
- Maintains 80 `Iotrack` buffers indexed by a 31-bucket hash table and a global LRU list.
- Each track holds `xf->sect2trk` sectors plus lazily-created `Iosect` wrappers for individually locked sectors.
- `getsect()` returns a read-populated sector; `getosect()` returns an output sector that can avoid reading when a full sector will be overwritten.
- `getiotrack()` finds or recycles an unreferenced track, flushing modified tracks before reuse and purging stale per-sector wrappers.
- `tread()` reads a whole track when no sector wrappers exist, or reads only missing sectors when some wrappers already exist.
- `twrite()` writes the full track, first filling missing stale sectors if necessary.
- `putsect()` merges sector flags into the parent track, handles immediate-write requests, decrements refs, and unlocks.
- `purgebuf()` flushes/purges all tracks belonging to an `Xfs`; `sync()` flushes all modified tracks.
- `iotrack_init()` initializes hash heads, LRU list, and empty track buffers.

## Interfaces And Dependencies
- Uses `devread()`/`devwrite()` for media I/O and `MLock` from `lock.c`.
- Sector and track structures are declared in `iotrack.h`.

## Notes
This cache is central to mutation correctness because FAT metadata operations often hold and modify sector buffers across helper calls. The simple locks are cooperative and detect misuse rather than blocking.
