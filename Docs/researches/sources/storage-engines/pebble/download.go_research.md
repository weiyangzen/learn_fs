# sources/storage-engines/pebble/download.go

## Purpose
Implements `DB.Download`, a high-priority mechanism for making spans independent of external SSTable backing files. It repeatedly discovers external tables overlapping requested key ranges and drives download compactions until no external tables remain in the target spans.

## Important APIs, Types, And Functions
`DownloadSpan` carries `[StartKey, EndKey)` plus `ViaBackingFileDownload`, which selects rewrite compaction versus raw backing-file copy. `DB.Download`, `createDownloadTasks`, `waitForDownloadTasks`, and `removeDownloadTasks` manage the public operation. `downloadSpanTask`, `downloadBookmark`, `newDownloadSpanTask`, `tryLaunchDownloadForFile`, and `tryLaunchDownloadCompaction` implement task progress. `launchDownloadResult` distinguishes launched work, no work, and task completion.

## Control Flow
`Download` checks closed/read-only state, emits `DownloadBegin`, creates tasks from the current version, installs them in `d.mu.compact.downloads`, schedules compaction, and waits on each task channel. On success it restarts discovery, because concurrent ingests may have introduced new external tables; on no tasks it emits a done `DownloadEnd`. A task scans levels top-down and by start key using `manifest.ScanCursor`. Each discovered external or compacting file creates a bookmark. Bookmarks are revisited after launched compactions finish or after other compactions release files.

## State And Persistence Behavior
The method persists data indirectly through compaction output and manifest version edits performed by the normal compaction machinery. Local state is transient: task channels, scan cursors, bookmark ranges, launch counters, and the `d.mu.compact.downloads` queue. `ViaBackingFileDownload` changes whether the compaction rewrites keys or copies a backing file byte-for-byte.

## Dependencies And Integration Points
Depends on manifest scan cursors, `objstorage.IsExternalTable`, compaction picking, `newCompaction`, `d.compact`, event listener `DownloadInfo`, compaction scheduling, and DB format/object-provider state. It integrates with external ingestion, virtual SSTables, excise cancellation, and compaction concurrency.

## Risks And Edge Cases
The cursor/bookmark logic must not miss files that move between levels, shrink through excise, or are already compacting. Cancelled download compactions are not terminal and force bookmark rescanning. Context cancellation and non-cancel compaction errors remove pending tasks. Concurrent external ingestion can cause restarts and means the API is best effort at the instant it returns.

## Test Signals
Covered by `download_test.go` datadriven task tests. Integration signals are `DownloadBegin`/`DownloadEnd`, `DownloadCompactionsLaunched`, compaction errors, and absence of external tables in downloaded spans.
