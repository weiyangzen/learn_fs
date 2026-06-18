# sources/sync-backup/kopia/snapshot/policy/retention_policy.go

Purpose: defines snapshot retention policy fields and computes why individual snapshot manifests should be retained. It also compacts retention and pin reason lists for display.

Important APIs/types/functions: `RetentionPolicy`, `RetentionPolicyDefinition`, `ComputeRetentionReasons`, `EffectiveKeepLatest`, `getRetentionReasons`, `CompactRetentionReasons`, `CompactPins`, and `SortRetentionTags`. Defaults are 10 latest, 48 hourly, 7 daily, 4 weekly, 24 monthly, 3 annual, and no identical-snapshot ignoring.

Control flow: computation finds max complete and overall start times, builds cutoffs, sorts manifests newest-first, assigns reasons to complete snapshots by unique latest/time buckets, then keeps recent or minimum-count incomplete snapshots with `"incomplete"`.

State and persistence: mutates each `snapshot.Manifest.RetentionReasons`; it does not save manifests. Merge records definition source for each optional field.

Dependencies and integration points: depends on `snapshot.SortByTime`, `fs.UTCTimestamp`, optional policy wrappers, and retention consumers that expire or display snapshots.

Risks and test signals: retention uses the latest complete snapshot as the anchor, so all-incomplete or clock-skewed sets need care. RLE compaction assumes numeric suffixes after the last dash. Tests cover latest, hourly/daily/monthly/weekly, incomplete, pins, and compaction.
