# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/icache.c

Implements the in-memory index-entry cache and arena-summary prefetch cache.

Key behavior:
- `initicache` sizes the main cache from memory, reserves about one eighth for summary cache, initializes clean/dirty/free lists, hash tables, and summary slots.
- Main cache stores `IEntry` records in free, clean LRU, and dirty lists.
- `icachelookup` checks main hash first, then summary-cache hash; summary hits are promoted into the main clean cache.
- `insertscore` inserts clean or dirty entries, updates newest dirty arena state for flush safety, schedules flushes, and marks Bloom for dirty inserts.
- `lookupscore` checks cache, then loads from disk index via `loadientry` and inserts a clean entry.
- `icachedirty` returns dirty entries in a hash range and below an address limit for index-section writers.
- `icacheclean` moves written dirty entries to the clean list and wakes waiters.
- `emptyicache` evicts clean entries and clears summary cache.
- Summary cache (`ISum`) tracks arena clump-info groups; first miss reserves a group, second miss loads `asumload` entries if prefetch is enabled.

Interactions:
- Used by read/write lookup paths, `icachewrite.c`, HTTP debug, and Bloom update.
- Summary cache depends on arena summary loading and `amapitoag`.

Notable details:
- Dirty insert without `AState` prints a warning; dirty address moving backward also prints.
- If no cache entry can be evicted, insertion waits after kicking dcache/icache flushes.
