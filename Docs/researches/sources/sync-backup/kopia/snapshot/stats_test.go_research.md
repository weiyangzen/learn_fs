# sources/sync-backup/kopia/snapshot/stats_test.go

Purpose: unit test for `snapshot.Stats.AddExcluded`.

Important APIs/types/functions: `TestStats`, `mockfs.NewDirectory`, `AddFile`, and `snapshot.Stats.AddExcluded`.

Control flow: creates a mock directory and a file, then runs two cases: excluding the directory should increment only `ExcludedDirCount`; excluding the file should increment `ExcludedFileCount` and `ExcludedTotalFileSize`.

State and persistence: all state is in memory through mock filesystem entries.

Dependencies and integration points: protects upload estimate and ignore handling code that relies on excluded counters.

Risks and test signals: test compares the entire `Stats` struct, so unintended changes to additional fields are caught. It does not cover concurrent atomic updates or other stats counters.
