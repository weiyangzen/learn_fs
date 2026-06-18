<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/stats/countsum.go -->
# sources/sync-backup/kopia/internal/stats/countsum.go

- Purpose: Tracks an atomic count and sum pair for simple concurrent statistics.
- Important APIs/types/functions: `CountSum`, `Add`, `Approximate`.
- Control flow: `Add` atomically increments count and sum and returns the new values; `Approximate` loads both independently.
- State and persistence: In-memory atomics only.
- Dependencies and integration points: Uses `sync/atomic`.
- Risks and edge cases: Count and sum are not read as one atomic snapshot, so returned pairs are approximate under concurrent updates.
- Test signals: No direct test in this subset; behavior is small and relies on atomic primitives.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/stats/countsum.go -->
