# sources/storage-engines/tikv/components/raftstore/src/store/worker/cleanup_sst.rs

## Purpose
This worker deletes imported SST files from the SST importer. It is part of raftstore/import cleanup after ingestion, cancellation, or stale import artifacts.

## Important APIs, Types, and Functions
- `Task::DeleteSst { ssts }` carries a list of `import_sstpb::SstMeta`.
- `Runner<E>` owns an `Arc<SstImporter<E>>`.
- `handle_delete_sst` iterates through SST metadata and invokes `SstImporter::delete`.

## Control Flow
The runner receives `DeleteSst`, formats the count for logging/display, and deletes each SST via the importer. Individual delete results are intentionally ignored, so the task is best-effort.

## State and Persistence Behavior
The worker mutates filesystem/importer state by deleting SST files tracked by `SstImporter`. It does not alter raft log or KV engine records directly. The importer is shared by `Arc`, so deletion coordinates with the importer implementation.

## Dependencies and Integration Points
It depends on `KvEngine`, `SstMeta`, `sst_importer::SstImporter`, and `tikv_util::worker::Runnable`. It is wired through `cleanup.rs` and used by raftstore paths that need asynchronous cleanup of import artifacts.

## Risks and Edge Cases
Errors from `importer.delete` are dropped, so missing files, permission issues, or transient filesystem failures are not surfaced by this runner. Callers that need stronger cleanup guarantees must observe importer state elsewhere.

## Test Signals
There are no direct tests in this file. Coverage comes from SST importer behavior and higher-level import/cleanup tests.
