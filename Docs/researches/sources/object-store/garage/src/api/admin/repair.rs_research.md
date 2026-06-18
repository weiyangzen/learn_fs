## sources/object-store/garage/src/api/admin/repair.rs

Purpose: implements admin-triggered local repair operations for tables, object/version/block references, stored blocks, scrub/rebalance commands, aliases, and resync queue cleanup.

Important APIs/types/functions: `RequestHandler for LocalLaunchRepairOperationRequest` dispatches by `RepairType`. `TableRepair` abstracts table-specific repair scans. `TableRepairWorker<T>` implements `garage_util::background::Worker` and scans the local underlying table store by byte cursor. `RepairVersions`, `RepairBlockRefs`, and `RepairMpu` implement consistency fixes for orphaned versions, block refs, and multipart uploads. `BlockRcRepair` recalculates block reference counters by walking both rc-table and block-ref-table keys.

Control flow: repair requests either schedule background workers through `admin.background.spawn_worker`, call full table syncers, send scrub commands to `BlockManager`, run foreground alias repair, or clear the resync queue in `spawn_blocking`. Table workers call `get_gt(&pos)`, decode entries, run `process`, count changed entries, advance cursor, and finish when no later key exists. `BlockRcRepair` processes up to `RC_REPAIR_ITER_COUNT` hashes per work tick.

State/persistence: mutates Garage metadata tables by inserting tombstoned or corrected entries, schedules block repair/rebalance workers, sends scrub control messages, recalculates persistent block reference counters, and may clear block resync queues.

Dependencies/integration: ties admin API request types to `Garage`, `garage_table`, `garage_model::s3::*` tables, `garage_block::manager::BlockManager`, and the background worker system.

Risks: repair operations are powerful and can delete metadata references when backlink checks fail. Local store scans depend on decode success and table key ordering. `wait_for_work` is unreachable, so these workers are expected to be continuously busy until done. `ClearResyncQueue` is foreground-triggered and destructive for retry state.

Test signals: no local tests; confidence comes from table schema invariants and operational logs reporting counts and repairs.
