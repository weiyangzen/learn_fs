# sources/sync-backup/kopia/snapshot/policy/logging_policy.go

Purpose: defines policy for controlling snapshot logging verbosity for directories and entries.

Important APIs/types/functions: `DirLoggingPolicy` has `Snapshotted` and `Ignored` levels. `EntryLoggingPolicy` adds `CacheHit` and `CacheMiss`. `LoggingPolicy` groups directory and entry policies. Definition structs track source fields. Each policy has a `Merge` method.

Control flow: merge fills unset `*LogDetail` fields from source policies and records definition source via `mergeLogLevel`. Top-level `LoggingPolicy.Merge` delegates to directory and entry merges.

State and persistence behavior: policy persists as JSON with pointer fields omitted when unset. Effective policies compute definition metadata in memory.

Dependencies/integration: consumed by snapshot upload logging. Depends on `LogDetail` and `snapshot.SourceInfo`.

Risks: explicit `LogDetailNone` must be a pointer to persist; non-pointer zero values disappear under omitempty in tests. Merge is first-value-wins and will not override a more specific log setting.

Test signals: `log_detail_test.go` covers JSON behavior; broader policy tests cover inheritance machinery.
