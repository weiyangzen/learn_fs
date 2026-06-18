# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/io.c

This file handles persistent storage, locking, title map management, and caching for wiki documents.

Storage layout:
- Wiki files live under `wikidir/d`.
- Per page:
  - `<n>`: current version.
  - `<n>.hist`: append-only full history.
  - `L.<n>`: page lock.
- Map:
  - `map`: append-only numeric id to title map.
  - `L.map`: map lock.

Cache model:
- `Wcache` entries keyed by page number cache current and history `Whist*`, qids, timestamps, and refs.
- Global cache hash has 64 buckets and nominal cap 128 entries.
- `getcache` returns current or full history, evicting least-recent unreferenced cache entries when needed.
- Cached file qids are refreshed after `Tcache` seconds.

Locking:
- `getlock` tries to create lock files with `DMEXCL`, retrying for up to about 200 seconds when errors mention `locked`.
- `readwhist` locks before reading and parsing a current/history file.

Map management:
- `currentmap` locks and reads `d/map`, validates `Maxmap`, builds `Mapel` entries, condenses/lowercases titles, sorts by title, and swaps global map under lock.
- `allocnum` validates title, checks duplicates, locks map, scans existing map directly to allocate next number, appends new entry, and forces map refresh.
- `nametonum` normalizes input by lowercase and underscore-to-space, then binary searches sorted map.
- `numtoname` finds map entry by numeric id.

Page write:
- `writepage` locks page, checks current version time against supplied edit base time, detects duplicate writes, appends all writes to history, marks conflicts with `X`, and only rewrites current file for conflict-free writes.
- Calls `voidcache` after writes/conflicts to invalidate cached page state.

Reference cleanup:
- `closewhist`, `freepage`, and `closemap` free refcounted wiki data.

Notable risks:
- Locking is file-based and intentionally described as a hack for read locks.
- `allocnum` comments acknowledge the ideal atomic map update is messy; it scans under lock and lets cache catch up.
- If no cache entry is evictable, the cache can grow beyond `Mcache`.
