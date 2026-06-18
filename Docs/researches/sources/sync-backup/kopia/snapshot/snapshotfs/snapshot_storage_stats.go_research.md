# sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_storage_stats.go

Purpose: computes per-snapshot new data and running total storage usage across a sequence of manifests.

Important APIs/types/functions: `CalculateStorageStats`, `snapshot.StorageUsageDetails`, `snapshot.StorageStats`, `TreeWalker`, and repository `VerifyObject`/`ContentInfo`.

Control flow: one `TreeWalker` and one unique-content `bigmap.Set` are reused across manifests. For each manifest, `unique` counters reset, the root is walked, each previously unseen object/content contributes to new and running totals, and the callback receives the manifest after `StorageStats` is populated.

State and persistence: mutates `Manifest.StorageStats` in memory only. Running totals and unique content set persist across the input manifest order.

Dependencies and integration points: depends on repository object verification, content metadata, and snapshot root conversion. Used by reporting and analysis features.

Risks and test signals: input manifest ordering matters for "new" data. The code assumes `manifests` is non-empty and uses `manifests[0].Source`. TreeWalker dedupes by object ID, so repeated identical snapshots produce zero new data.
