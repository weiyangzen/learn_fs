# sources/sync-backup/restic/cmd/restic/cmd_diff.go

Purpose: implements `restic diff`, comparing two snapshots or snapshot subfolders and reporting file additions, removals, modifications, type changes, metadata updates, and summary statistics.

Important APIs/types/functions: `DiffOptions` controls metadata reporting. `Comparer` owns repository access and output callbacks. `Change`, `DiffStat`, and `DiffStatsContainer` model output and JSON statistics. `diffTree`, `printDir`, `collectDir`, `addBlobs`, and `updateBlobs` traverse trees and compute changed blob stats. `runDiff` wires snapshot loading, index loading, output mode, and final stats.

Control flow: requires two snapshot descriptors, opens a read lock, memoizes snapshot listing, finds snapshots/subfolders, loads index, resolves tree directories, recursively dual-iterates tree nodes, prints changes, tracks blob sets before/after/common, updates stats for non-common blobs, and prints text or JSON summary. Quiet mode suppresses individual changes.

State/persistence: read-only except locks/cache. It loads tree blobs and index metadata.

Dependencies/integration: `internal/data` tree iterators, repository blob lookup, UI progress, JSON encoder, and snapshot descriptor parsing.

Risks/test signals: bitrot marker depends on content changes with unchanged metadata and can be affected by backup ignore flags. Recursive error handling prints some child errors without aborting. Integration tests validate text regexes, quiet behavior, JSON change/stat records, and summary counts.
