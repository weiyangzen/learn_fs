# sources/storage-engines/wiredtiger/src/conn/conn_layered.c

## Purpose
This file owns connection-level disaggregated and layered-table coordination. It configures disaggregated storage, manages leader/follower role transitions, initializes shared metadata, queues metadata operations for checkpoint publication, creates missing stable tables, processes metadata updates into the shared metadata table, handles clean startup-directory behavior for disaggregated mode, and advances global disaggregated checkpoints.

## Important APIs, Types, and Functions
`__wti_disagg_conn_config` parses initial and reconfigure settings for `disaggregated.*`, opens the page log, opens special PALI handles for shared metadata and key provider data, initializes the layered table manager, picks up configured checkpoints, begins or abandons checkpoints for leaders, sets page-delta options, `lose_all_my_data`, and drain thread count, and performs role step-up/step-down on reconfigure.

`__wt_disagg_enqueue_metadata_operation`, `__wti_disagg_shared_metadata_queue_prune`, `__wti_disagg_table_latest_create_remove`, `__wt_disagg_shared_metadata_queue_publish`, `__wt_disagg_shared_metadata_queue_drop_size`, and `__wt_disagg_shared_metadata_queue_process` manage `conn->disaggregated_storage.shared_metadata_qh`. Queue entries capture stable, table, colgroup, and layered metadata values, a schema epoch, a metadata operation (`CREATE`, `UPDATE`, `REMOVE`), and a deferred bit.

`__layered_create_missing_stable_tables` and helpers create stable constituents from layered metadata after follower step-up. The schema-epoch path replays queued create entries newer than the last stable checkpoint while skipping creates followed by removes. The legacy path scans local metadata for `layered:` entries and creates missing stable tables best-effort.

`__disagg_step_up`, `__disagg_step_down`, `__disagg_abandon_checkpoint`, `__disagg_begin_checkpoint`, and `__disagg_restart_checkpoint` implement role transitions and checkpoint state. `__wt_disagg_advance_checkpoint` completes a global checkpoint through the page log and starts the next one. `__wti_ensure_clean_startup_dir` removes or rejects stale local WiredTiger files for disaggregated "lose all my data" startup.

## Control Flow and Behavior
On initial config, the connection records the configured role, opens the page log, opens PALI handles for the shared metadata table and key-provider table, and, if disaggregated mode is active, rejects read-only mode, initializes the layered table manager, optionally abandons incomplete checkpoints as leader, creates the shared metadata table, picks up a supplied checkpoint, or as a startup leader attempts to find and pick up the latest complete checkpoint before beginning a new checkpoint.

On reconfigure, a follower may pick up `disaggregated.checkpoint_meta`. Role changes happen under the checkpoint lock. Step-up sets the leader flag first, abandons any incomplete checkpoint, begins a new checkpoint, creates missing stable tables, drains ingest tables into stable tables, and marks the shared disk cache read-only with a timestamp. Step-down marks open disaggregated btrees read-only and outdated under the handle-list read lock before clearing leader state, clears the metadata queue, and reactivates or initializes the shared disk cache for follower use.

Metadata operations are enqueued while the schema lock is held. Schema operations start deferred so operations already present at checkpoint start are processed at checkpoint end, while concurrent operations wait for a later checkpoint. Queue processing holds the schema lock and queue lock, skips deferred or future-epoch entries, handles create/remove pairs for tables that never had stable metadata, applies operations to the shared metadata table, and frees processed entries. It panics on API violations where a published create needs shared metadata but the stable table was never created before a later drop.

Checkpoint advance is leader-only. On success it formats checkpoint metadata containing metadata LSN, checksum, database size, version, and compatible version, calls `pl_complete_checkpoint`, stores the checkpoint timestamp, logs completion, and begins the next checkpoint. On unsuccessful checkpoint it skips completion but still begins the next checkpoint.

## State and Persistence Behavior
Persistent state includes the disaggregated shared metadata table, PALI page-log checkpoint completion records, stable table metadata copied to shared storage, local metadata updated by checkpoint pickup, and the local filesystem cleanup behavior in disaggregated mode. In-memory state includes role, page-log handles, metadata queue entries, last materialized LSN, last checkpoint metadata LSN/checksum/root/timestamps, database size, page-delta config, shared disk cache state, and drain thread count.

Schema epochs are the consistency boundary for metadata publication. `WT_SCHEMA_EPOCH_UNPUBLISHED` entries are published later by `__wt_disagg_shared_metadata_queue_publish`; queue pruning removes entries at or below a completed checkpoint's schema epoch. The leader's checkpoint lock serializes role transitions, checkpoint begin/complete, and checkpoint abandonment.

## Dependencies and Integration Points
This file integrates with schema creation, metadata cursors, the layered table manager, ingest-table drain code in `conn_layered_ingest.c`, checkpoint pickup in `conn_layered_checkpoint_pick_up.c`, page-log helpers in `conn_layered_page_log.c`, key provider loading, shared disk cache, block-disaggregated metadata, checkpoint, transaction-global timestamps, and connection reconfiguration.

It is also called by schema paths that enqueue shared metadata operations, checkpoint paths that process/drop-size/prune the queue, startup code that cleans directories, and role-management tests that reconfigure `disaggregated.role`.

## Risks
Role transition ordering is high risk. Step-up sets leader mode before abandoning/restarting checkpoints and draining ingest tables because later operations depend on leader behavior. If the checkpoint lock is not held, a checkpoint can observe half of a role transition. Step-down must make btrees read-only before clearing leader state to prevent eviction or split paths from dirtying pages in the follower window.

Shared metadata queue ordering and schema epoch validation are critical. A create followed by remove can be safely skipped only when no checkpoint needed the table in between. Update operations must not publish stable data before the table create is visible. Missing stable values, future epochs, or out-of-order epochs can cause followers to miss metadata or require a panic to avoid silent inconsistency.

Startup cleanup can delete local WiredTiger files when `lose_all_my_data` and local file action permit it. The filter must keep lock and stat files as intended while removing files that would make disaggregated startup read stale local state.

## Test Signals
Relevant tests include `test_layered_stepup01.py`, `test_layered_stepup02.py`, layered follower/cursor/fast-truncate/prepare suites, disaggregated model and cppsuite failover tests, and format disaggregated configurations with `disagg.drain_threads` and `preserve_prepared`. Stats include role, step-up/down time, checkpoint metadata apply/defer counts, database size, checkpoint completion, and abandon checkpoint success/failure. Failure-injection signals include `WT_TIMING_STRESS_FAILPOINT_DISAGG_CHECKPOINT_QUEUE_DRAIN` and panic paths for bad queue ordering.
