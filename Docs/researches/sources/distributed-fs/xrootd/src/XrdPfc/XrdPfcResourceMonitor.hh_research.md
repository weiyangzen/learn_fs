# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcResourceMonitor.hh

## Purpose
Declares the resource-monitor subsystem for proxy-cache usage accounting and purge decisions. It defines event queues, access tokens, scan coordination, registration APIs called by `File`, and heartbeat/purge helpers.

## Important APIs, Types, and Functions
- Template `Queue<ID, RECORD>` provides producer write queue, consumer read queue, atomic-ish swap, and shrink helpers under external locking.
- `AccessToken` ties a file open to filename, last stats queue position, swap generation, and resolved `DirState`.
- `OpenRecord`, `CloseRecord`, and `PurgeRecord` are queue payloads.
- Registration APIs: `register_file_open`, `register_file_update_stats`, `register_file_close`, `register_file_purge`, and multi-file purge variants.
- Actions: `process_queues`, `heart_beat`, `perform_initial_scan`, `scan_dir_and_recurse`, `perform_purge_check`, `perform_purge_task`, and cleanup.
- Scan coordination: `CrossCheckIfScanIsInProgress` and `m_dir_scan_open_requests`.

## Control Flow
File objects register events into queues under `m_queue_mutex`. The heartbeat swaps queues, increments `m_queue_swap_u1`, and consumes records in open, update, close, purge order. Initial scan coordination lets file opens wait while their directory is checked or later released after scan completion.

## State and Persistence Behavior
Persistent state is indirect: the monitor may write snapshot files and schedule purges. In-memory state includes `DataFsState`, access-token freelist, event queues, current usage, scan flags, and purge task timestamps/flags.

## Dependencies and Integration Points
Depends on `XrdPfcStats`, `XrdSysPthread`, `XrdOss`, and forward-declared directory/snapshot/purge structures. It is tightly integrated with `File`, `Cache`, `FsTraversal`, and purge plugin flows.

## Risks and Test Signals
Risks include token vector growth/reuse bugs, queue iterator constness oddities, stats updates before open resolution, and stale `DirState*` in purge records. Tests should validate queue coalescing, token release on close, scan wait signaling, and purge active/complete flags.
