# sources/storage-engines/pebble/obsolete_files_test.go

Purpose: This file tests obsolete-file cleanup behavior, including a regression for path-qualified stat calls and data-driven cleaner behavior.

Important tests and helpers: `TestScanObsoleteFilesUsesFullPath` opens a DB under non-root directory `db`, forces MANIFEST/OPTIONS rotation, wraps the memory FS in `statTrackingFS`, reopens the DB to trigger `scanObsoleteFiles`, and fails if `Stat` for MANIFEST/OPTIONS is called with a bare filename instead of `db/<name>`. `statTrackingFS` records such calls. `TestCleaner` is data-driven over `testdata/cleaner` and supports `open`, `batch`, `compact`, `flush`, `close`, `list`, and `create-bogus-file`.

Control flow and state: `TestCleaner` keeps a map of open DBs, uses a logging memory FS, can configure archive or readonly cleaning modes, disables asynchronous table stats output, and waits for cleanup to stabilize expected logs. It exercises deletion through normal DB write/flush/compact/open/close workflows rather than direct calls.

Dependencies and integration: The tests use full `pebble.Open`, `Options`, WAL directories, cleaners, batch helpers, compaction, and VFS logging. They validate cleanup as an integrated DB behavior.

Risks and test signals: The path regression test protects non-root and non-local filesystems where bare names resolve incorrectly. The data-driven test catches cleaner ordering and behavior changes, but expected logging can be sensitive to unrelated FS operation changes.
