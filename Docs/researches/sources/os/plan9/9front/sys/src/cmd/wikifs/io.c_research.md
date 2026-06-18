# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/io.c

Storage, locking, caching, map, lookup, and write implementation for the file-backed wiki used by `wikifs`.

Key behavior:
- Stores each document as `d/nnn` current file, append-only `d/nnn.hist` history, `d/L.nnn` lock, plus append-only `d/map` title mapping protected by `d/L.map`.
- `getlock()` acquires exclusive lock files with retry and timeout.
- `readwhist()` reads history/current files under the lock using `Brdwhist()`.
- `getcache()` maintains up to 128 cached page entries, refreshing current/history data by qid/version and evicting least-recently used unreferenced entries.
- `currentmap()` loads and sorts the title map, caching by qid/version and enforcing `Maxmap`.
- `allocnum()` validates and normalizes titles, rejects reserved names and bad characters, appends a new map entry under lock, and refreshes the map.
- `nametonum()` lowercases and converts underscores to spaces, then binary-searches the sorted map; `numtoname()` does reverse lookup.
- `writepage()` appends a new revision to history, detects update conflicts by comparing the caller's base timestamp with the current file, records conflicting writes with `X`, and updates the current file only for non-conflicting writes.

Notable dependencies:
- Wiki history parser, page formatter, `wdir.c` relative file wrappers, Plan 9 locks, Bio, String library.

Research notes:
- The lock file is used for both read and write exclusion because the backing filesystem lacks read/write locks.
- `writepage()` ignores duplicate writes when the new body after metadata matches the current body.
- Cache invalidation is explicit after writes through `voidcache()`.
