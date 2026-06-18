## sources/storage-engines/pebble/tool/db_analyze_data.go

Purpose: implements `db analyze-data`, a sampling tool that reads SSTables and feeds them into `compressionanalyzer.FileAnalyzer` to estimate compression behavior and write progressive CSV output.

Important APIs/types/functions: `runAnalyzeData` drives listing, sampling, progress reporting, throttling, and CSV persistence. `analyzeSSTable` opens a selected object and analyzes it. `analyzeSaveCSVFile` writes analyzer buckets. `dbStorage` abstracts local VFS and remote storage. `vfsStorage` lists local files, filters files modified in the last 15 seconds, and opens object-storage readables. `remoteStorage` lists and opens cloud objects while faking size as 1 MiB. `fileSet`, `fileInSet`, `makeFileSet`, `Refresh`, `Sample`, `Remaining`, and `samplingKey` implement weighted sampling without replacement using the Efraimidis-Spirakis algorithm. `isTTY` and `clearScreen` control interactive progress.

Control flow: the command detects remote paths by `://` and requires `DBRemoteStorageFn`; otherwise it wraps `d.opts.FS`. It builds a random `fileSet`, optionally creates a token-bucket read limiter, and loops until sample percent, timeout, or exhausted files. Every ten seconds, or on stop, it prints bucket summaries, writes CSV, and refreshes the local file list. Sampling ignores deleted or transiently unreadable files and continues after reporting non-not-exist errors.

State and persistence: persistent output is the CSV file required by the command flag. In-memory state tracks sampled files and bytes; local file sets preserve already-sampled entries across refreshes. No DB is opened, which allows analysis against directories or remote object stores.

Dependencies and integration: uses Pebble filename parsing, VFS, remote storage, object-storage readables, `compressionanalyzer`, `tokenbucket`, configured comparers/mergers/key schemas, and the `dbT.analyzeData` flags installed in `db.go`.

Risks: remote object sizes are synthetic, so sampling percentages are file-count based and bytes printed are less meaningful. Very large local SSTables over 512 MiB are skipped to reduce memory pressure. `Refresh` contains a dead `if err != nil` check after `Size`, relying on size zero for errors. The command tolerates live-directory churn but may underreport if files are young or repeatedly removed.

Test signals: `TestFileSetSampling` statistically verifies size-weighted first-sample behavior and uses a wrapper to make memfs files old enough to pass the 15-second filter.
