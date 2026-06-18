# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/icache.c

Implements the in-memory index-entry cache plus an arena-summary prefetch cache. The main cache stores `IEntry` records by score/type in hash buckets and maintains circular free, clean LRU, and dirty lists.

`initicache()` sizes entry and summary-cache populations from memory budget. `icachelookup()` checks dirty/clean entries first, then summary-cache entries, promoting summary hits into the main clean cache. `lookupscore()` fills misses from disk via `loadientry()`.

`insertscore()` inserts clean or dirty entries. Dirty inserts update the latest `AState`, schedule index-cache writeback, and mark the Bloom filter. Clean inserts may trigger two-step summary prefetch: first miss reserves a summary slot, second miss loads arena group summaries via `asumload()`.

`icachedirty()` returns dirty entries in a hash range below a committed arena-address limit for writeback. `icacheclean()` marks written dirty entries clean and wakes waiters. `emptyicache()` evicts clean entries and clears summary caches.
