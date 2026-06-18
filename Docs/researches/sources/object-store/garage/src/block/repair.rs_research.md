# sources/object-store/garage/src/block/repair.rs

Purpose: implements block repair, data scrub, rebalance, and block-store enumeration workers.

Important APIs/types/functions: `RepairWorker`, `ScrubWorker`, persisted `ScrubWorkerPersisted`, `ScrubWorkerCommand`, `RebalanceWorker`, `BlockStoreIterator`, `BsiTodo`, and helpers `randomize_next_scrub_run_time`, iterator `progress`/`next`.

Control flow: `RepairWorker` phase 1 batches RC-table hashes into the resync queue to avoid SQLite iterator/write deadlock, then phase 2 walks disk blocks and enqueues them too. `ScrubWorker` is a periodic/manual worker with running/paused/finished state, persisted checkpoints every minute, tranquility throttling, and command handling for start/pause/resume/cancel. It reads every block and increments persistent corruption count on `CorruptData`. `RebalanceWorker` scans blocks, moves files outside their primary location by re-reading/re-writing, and finally persists a layout without secondary locations.

State and persistence: scrub state persists in `scrub_info`, migrating from v081 to v082 with `time_next_run_scrub` and iterator checkpoint. Rebalance updates `data_layout`. Repair feeds persistent resync queue entries. Disk iterator state is serializable for checkpointing.

Dependencies and integration points: depends on `garage_util::background::Worker`, `PersisterShared`, `Tranquilizer`, time/data/error utilities, tokio filesystem/channel/watch, and the block manager. Admin repair commands trigger these worker paths through local admin APIs.

Risks: block-store enumeration assumes data directory structure and 64-hex filenames; extra files are mostly ignored but malformed block-like filenames can be considered. Directory progress division uses discovered entry count; empty directory branches need care. Repair phase batching is tailored around SQLite locking behavior. Rebalance removes secondary locations only after its scan completes, so interrupted runs leave conservative layout state.

Test signals: no local unit tests. Operational tests should cover scrub checkpoint resume, pause/cancel commands, corrupted block detection, SQLite repair batching, rebalance of secondary locations, and iterator progress invariants.
