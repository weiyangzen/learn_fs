# sources/security-integrity/cryfs/crates/check/src/runner.rs

Purpose: This file implements the core filesystem checking traversal. `RecoverRunner` is a `BlockstoreCallback` that receives the configured blockstore stack, enumerates all blocks, traverses reachable blobs and nodes, checks unreachable nodes, finalizes all checks, and returns `Vec<CorruptedError>`.

Important APIs and flow: `callback` parses the root blob id from config, lists all node ids via `all_blocks`, creates `AllChecks`, builds an `FsBlobStore` over `BlobStoreOnBlocks`, calls `check_all_reachable_blobs`, then unwraps to `DataNodeStore` and calls `check_all_nodes_of_reachable_blobs`. Finally it removes processed reachable nodes from the all-node set and calls `check_all_unreachable_nodes`. Each phase uses progress bars/spinners and explicit async drops on error or completion.

Traversal details: Reachable blob traversal starts at the root `BlobReferenceWithId` and recursively spawns child blob checks for directory entries through `task_queue::run_to_completion(MAX_CONCURRENCY)`. `ProcessedItems` detects repeated blob ids; if repeated observations differ, the run aborts with `FilesystemModified`, otherwise duplicate-reference assertions are added. Node traversal similarly spawns child data-node tasks from inner nodes, tracks repeated node ids, and asserts duplicate-node diagnostics.

State and persistence: Runtime state is in-memory: `HashSet<BlockId>` for initial block ids, `ProcessedItems` mutex maps for blobs and nodes, `SeenBlobInfo` and `SeenNodeInfo` summaries, and `AllChecks`. The blockstore is wrapped by higher layers outside this file and explicitly dropped asynchronously. No repair or write-back occurs.

Dependencies and integration: The runner integrates blockstore, blobstore, fsblobstore, config, progress UI, async-drop, task queue, and all check modules. It relies on `AllowIntegrityViolations` setup in `cli.rs` so corrupt blocks can be observed and reported rather than aborting too early.

Risks and test signals: TODOs identify function size, concurrency tuning, duplicate code between seen branches, missing blob type checks, possible double-loading of directory nodes, and progress-bar length accuracy. The runner treats mid-run appearance/disappearance or changed summaries as `FilesystemModified`; users must keep vaults unmounted and stable during checks. `MAX_CONCURRENCY` is fixed at 100.
