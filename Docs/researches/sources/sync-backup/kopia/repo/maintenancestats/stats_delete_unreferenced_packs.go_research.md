# sources/sync-backup/kopia/repo/maintenancestats/stats_delete_unreferenced_packs.go

Purpose: records counts and sizes for pack garbage collection.

Important APIs/types/functions: `DeleteUnreferencedPacksStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes unreferenced, deleted, and retained pack counts/sizes into content logs and returns a readable summary.

State/persistence behavior: stored in maintenance schedule extras after pack GC tasks.

Dependencies/integration: produced by `DeleteUnreferencedPacks` and interpreted by `BuildFromExtra`.

Risks/test signals: fields distinguish retained from deleted, which is important for dry-run and safety-preserved blobs. Builder tests cover JSON.
