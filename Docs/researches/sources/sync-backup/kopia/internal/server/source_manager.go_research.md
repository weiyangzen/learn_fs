<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/source_manager.go -->
# sources/sync-backup/kopia/internal/server/source_manager.go

- Purpose: Implements the per-source snapshot scheduling/upload state machine used by the server.
- Important APIs/types/functions: `sourceManager`, `sourceManagerServerInterface`, `Status`, `start`, `runLocal`, `runReadOnly`, `scheduleSnapshotNow`, `upload`, `cancel`, `pause`, `resume`, `stop`, `snapshotInternal`, `refreshStatus`, `uitaskProgress`, `newSourceManager`.
- Control flow: A source starts by refreshing policy/snapshot status, then runs local mode waiting for snapshot requests or remote read-only mode. Upload requests enqueue a buffered signal, local mode runs a server snapshot task, and `snapshotInternal` opens the local filesystem, creates a repository write session, constructs an uploader and policy tree, reports UI progress, saves a snapshot unless identical snapshots are ignored, and applies retention.
- State and persistence: Mutex-protected state tracks current uploader, scheduling policy, status, next snapshot time, last snapshots, pause flag, current task, last attempted time, and read-only mode. Durable state is repository policy and snapshot manifests.
- Dependencies and integration points: Integrates `fs/localfs`, `serverapi`, `uitask`, `notifydata`, `repo.WriteSession`, `snapshot`, `policy`, and `upload`.
- Risks and edge cases: Cancellation depends on uploader registration order, refresh failures collapse into `FAILED` without detail, and failed upload backoff only changes an already-known next snapshot time.
- Test signals: Covered indirectly by server/scheduler/API tests; progress callbacks are tied to upload package behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/source_manager.go -->
