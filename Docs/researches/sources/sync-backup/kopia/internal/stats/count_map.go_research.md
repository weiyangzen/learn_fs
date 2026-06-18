<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/stats/count_map.go -->
# sources/sync-backup/kopia/internal/stats/count_map.go

- Purpose: Implements a generic concurrent map of atomic uint32 counters.
- Important APIs/types/functions: `CountersMap`, `Increment`, `add`, `Length`, `Get`, `Range`, `CountMap`.
- Control flow: Increment first attempts `Load`, then `LoadOrStore` for new counters, increments length only for new keys, and atomically adds to the pointed counter. Range and CountMap iterate over `sync.Map`.
- State and persistence: In-memory `sync.Map` plus atomic length/counters; no removal or persistence.
- Dependencies and integration points: Uses `sync` and `sync/atomic`.
- Risks and edge cases: Length and snapshots are approximate under concurrent mutation; counters can overflow because `add` has no overflow guard.
- Test signals: `count_map_test.go` covers missing keys, new/existing increments, add, range, length, early stop, snapshot, and concurrent increments.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/stats/count_map.go -->
