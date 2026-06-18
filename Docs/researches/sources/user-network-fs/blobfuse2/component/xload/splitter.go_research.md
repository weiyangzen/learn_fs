## sources/user-network-fs/blobfuse2/component/xload/splitter.go

Purpose: Splits remote files into block-sized download work items, writes completed chunks to a local cache file, and optionally validates MD5 consistency.

Important APIs and flow: `newDownloadSplitter` validates dependencies, stores the block pool, local path, file locks, and MD5 flag, and initializes a thread pool. `Process` locks non-priority file requests, skips existing same-size files, opens/creates the local file, handles zero-byte files, truncates to target size, schedules one `WorkItem` per block on the data manager, and collects responses on a channel. A collector goroutine writes each block to the correct offset, releases blocks, cancels remaining work on error, and records stats. After success it applies atime/mtime and calls `checkConsistency` when enabled.

State and persistence: Writes cache files under `ds.path`; failed downloads are deleted. Uses `BlockPool` for transient buffers and `common.LockMap` to coordinate lister and on-demand open paths.

Dependencies and integration: Requires a next `XComponent` data manager and remote metadata from lister/xload. Uses `common.GetMD5` and OS file operations.

Risks: Disk I/O stats mark `Success:false` for disk writes, likely skewing metrics. No retry on block failure or MD5 mismatch. Existing same-size files are trusted unless MD5 validation is reached through a fresh download. Tests cover present-file handling, full chained download, and MD5 comparison.
