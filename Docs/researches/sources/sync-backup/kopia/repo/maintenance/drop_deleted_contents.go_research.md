# sources/sync-backup/kopia/repo/maintenance/drop_deleted_contents.go

Purpose: drops old deleted content entries from indexes during full maintenance.

Important APIs/types/functions: `dropDeletedContents`, `content.CompactOptions`, and `CompactIndexesStats`.

Control flow: calls `ContentManager().CompactIndexes` with `DropDeletedBefore` and `DropDeletedExtraMargin` derived from safety, then returns stats indicating the cutoff time.

State/persistence behavior: rewrites/compacts repository content indexes so deleted entries older than a safe cutoff are removed from persisted index state.

Dependencies/integration: invoked by `runTaskDropDeletedContentsFull` after `findSafeDropTime` decides that enough snapshot-GC history exists.

Risks/test signals: the safety cutoff is critical; dropping too early can make race-recovered contents unreachable. Covered by maintenance safety and timing tests around safe drop time.
