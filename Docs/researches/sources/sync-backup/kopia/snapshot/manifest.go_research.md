# sources/sync-backup/kopia/snapshot/manifest.go

Purpose: defines persistent snapshot manifest and directory-entry schemas plus sorting/grouping helpers.

Important APIs/types/functions: `Manifest` stores ID, source, description, times, stats, incomplete reason, root entry, tags, storage stats, and pins. `UpdatePins`, `RootObjectID`, `Clone`, `GroupBySource`, and `SortByTime` are key methods/functions. Types include `EntryType`, `Permissions`, `DirEntry`, `DirManifest`, `StorageStats`, and `StorageUsageDetails`.

Control flow: `UpdatePins` merges additions/removals through a map, sorts pins, and reports whether anything changed. `Permissions` marshals non-zero values as octal strings and unmarshals using `strconv.ParseInt` with base detection. `Clone` shallow-copies manifest/entry and deep-copies `DirSummary`. Grouping maps manifests by `SourceInfo`; sorting clones input and orders by start time with end time tie-breaker, reversible via the `reverse` flag.

State and persistence behavior: JSON tags define durable manifest format. `RetentionReasons` is not persisted. `StorageStats` is persisted when populated but comments note ordering-dependent usage values. Atomic-check annotations mark storage usage counters.

Dependencies/integration: depends on `fs`, repository `manifest.ID`, and `object.ID`. Directory manifests are stored as object streams by snapshot upload/read paths.

Risks: `Permissions.MarshalJSON` returns `nil, nil` for zero permissions, which relies on JSON encoding behavior and may produce surprising output if used outside omitempty contexts. `Clone` does not deep-copy maps/slices like tags or pins. Storage stats depend on traversal order and should not be treated as absolute independent facts.

Test signals: sorting/grouping/pin behavior may be covered elsewhere; this file is schema-heavy and validated indirectly by snapshot save/load tests.
