# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcResourceMonitor.cc

## Purpose
Implements `ResourceMonitor`, the background monitor for proxy-cache directory usage, per-file access stats, snapshots, and purge scheduling. It builds an initial `DirState` tree, ingests event queues from active files, writes directory-stat snapshots, computes purge needs, and schedules purge jobs.

## Important APIs, Types, and Functions
- `CrossCheckIfScanIsInProgress()` blocks file opens during initial namespace scan until their directory has been checked.
- `perform_initial_scan()` traverses the OSS namespace, builds baseline usage, handles pending open requests, and propagates initial usage upward.
- `process_queues()` swaps producer queues and applies open/update/close/purge records to `DirState`.
- `heart_beat()` is the infinite scheduler loop for queue processing, filesystem state updates, snapshot writing, and purge checks.
- `fill_sshot_vec_children()` and `fill_pshot_vec_children()` serialize `DirState` tree views into snapshot vectors.
- `update_vs_and_file_usage_info()` refreshes data/meta space totals and current file usage.
- `get_file_usage_bytes_to_remove()` computes bytes to remove from configured file-usage and disk-usage watermarks.
- `perform_purge_check()` creates `DataFsPurgeshot`, decides whether purge is required, and schedules an async purge job.
- `perform_purge_task()` runs `OldStylePurgeDriver`; cleanup marks purge completion and clears protection.

## Control Flow
Startup calls `init_before_main`, then `main_thread_function` performs an initial scan and processes queued open/update events that occurred during scanning. The heartbeat then sleeps until the nearest scheduled event, always processes queues, updates disk usage, optionally updates and resets directory stats, writes `/pfc-stats/DirStat.json`, and performs purge checks. Purge tasks run in scheduler jobs and communicate completion back through `m_purge_task_cond`.

## State and Persistence Behavior
The monitor owns `DataFsState`, access-token tables, write/read queues, current file usage in `st_blocks`, scan coordination lists, and purge-task status. It writes directory-stat JSON snapshots through OSS when enabled and updates in-memory directory usage/stat trees. Purge tasks persistently delete cache files indirectly through `OldStylePurgeDriver`.

## Dependencies and Integration Points
Depends on `Cache`, `FsTraversal`, `DirState`, snapshot/purgeshot structures, `PurgePin`, `XrdOss`, and trace macros. `File` calls `register_file_open`, `register_file_update_stats`, `register_file_close`, and purge registration methods. Purge code reports deletions back to this monitor.

## Risks and Test Signals
High-risk areas are scan/open coordination, token reuse, queue swap/update ordering, directory pointer validity during purge, fatal `_exit(1)` on `StatVS` failure, and purge scheduling while a prior task is active. Tests should simulate opens during initial scan, high-volume stat updates coalescing by token, purge records by pointer/path/LFN, snapshot vector parent ranges, watermark calculations, and purge task lifecycle.
