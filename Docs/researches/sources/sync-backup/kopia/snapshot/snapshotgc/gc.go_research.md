# sources/sync-backup/kopia/snapshot/snapshotgc/gc.go

Purpose: snapshot-aware garbage collection that finds content no longer referenced by snapshot manifests, optionally deletes it, and repairs referenced content that was previously marked deleted.

Important APIs/types/functions: `findInUseContentIDs`, `Run`, `runInternal`, `findUnreferencedAndRepairRereferenced`, and `buildGCResult`.

Control flow: GC loads all snapshot manifests, walks each root with `snapshotfs.TreeWalker`, verifies objects to collect referenced content IDs, then iterates all contents including deleted entries. Manifest/system contents are counted separately. Referenced deleted contents are undeleted; unreferenced recent contents are protected by safety age; older unreferenced contents are logged and optionally deleted.

State and persistence: can undelete and delete repository content and flushes periodically and at the end. Maintenance run statistics are recorded through `maintenance.ReportRun`.

Dependencies and integration points: used by full snapshot maintenance, integrates with content logs, maintenance safety parameters, repository content manager, and maintenancestats.

Risks and test signals: safety window depends on maintenance start time and content timestamps. Without `gcDelete`, finding unused content returns an error after stats. Tests cover simple deletion, min-age protection, and undelete of reused referenced content.
