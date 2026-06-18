# sources/sync-backup/kopia/repo/recently_read.go

Purpose: provides a small thread-safe ring/set cache for content IDs recently read by repository code.

Important APIs/types/functions: `recentlyRead` stores `contentList`, `next`, and `contentSet` under a mutex. Methods are `add(content.ID)` and `exists(content.ID)`.

Control flow: `add` is nil-safe, lazily initializes fixed-size storage based on `numRecentReadsToCache`, deletes the evicted ring slot from the set, inserts the new ID, and advances the ring pointer. `exists` is nil-safe and checks the set under the same mutex.

State and persistence behavior: purely in-memory, non-persistent, bounded by the configured ring length. Duplicate adds keep the set entry and still advance the ring.

Dependencies/integration: depends on `repo/content.ID` and a package-level `numRecentReadsToCache` defined elsewhere. It is intended as a helper for avoiding redundant recent-read work.

Risks: duplicate content IDs in the ring can cause one eviction to delete the set entry even if the same ID appears in another slot, making this a lossy recency hint rather than an exact cache. That is acceptable only if callers treat it as advisory.

Test signals: no direct tests in this file; expected to be covered indirectly by cache/read behavior.
