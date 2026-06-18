<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/storagestats/storage_stats.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/storagestats/storage_stats.go

This file logs disk usage snapshots for directories created by the multiclient framework. `DirectorySize` records a path and byte count; `LogStorageStats` collects sizes, JSON-encodes them, and writes a timestamped log file under a package-level path.

`collectDirectorySizes` iterates configured directories, `getSize` recursively walks each directory with `filepath.WalkDir` and sums non-directory sizes, and `getLogFilePath` lazily creates one shared log path in the current working directory. The client ID from the context is included in the filename.

State is the package-global `logFilePath`, so repeated calls overwrite the same file rather than creating before/after files. Dependencies are multiclient context identities and OS filesystem walking. Risks include a race on `logFilePath`, large repo walks slowing test setup/teardown, and failure on transient deleted paths. Test signals are manual/log artifacts rather than assertions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/storagestats/storage_stats.go -->
