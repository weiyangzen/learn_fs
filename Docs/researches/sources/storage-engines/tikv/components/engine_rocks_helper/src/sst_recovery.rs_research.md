<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks_helper/src/sst_recovery.rs -->
# sources/storage-engines/tikv/components/engine_rocks_helper/src/sst_recovery.rs

## Purpose
`sst_recovery.rs` implements a worker runner that reacts to damaged RocksDB SST file names, maps damaged file key ranges to overlapping regions in raftstore metadata, deletes files that no longer overlap live regions, and panics defensively when recovery is unsafe or stuck.

## Important APIs, Types, and Functions
`RecoveryRunner` owns a `RocksEngine`, shared `StoreMeta`, `damaged_files`, `max_hang_duration`, and `check_duration`. It implements `Runnable<Task = String>` and `RunnableWithTimer`. `RecoveryRunner::new` constructs it.

`FileInfo` records damaged file name, smallest/largest keys, and scheduling start time. `generate_scheduling_tasks` finds the live file by path, validates key ranges, enforces `MAX_DAMAGED_FILES_NUM`, checks overlap, and records the file. `check_damaged_files` periodically drops handled files or panics on timeout. `check_overlap_damaged_regions` updates damaged ranges in `StoreMeta`; if no overlap remains, it deletes files in range and verifies the file disappeared.

## Control Flow
Worker `run` receives an SST path and calls `generate_scheduling_tasks`. Duplicate paths already in `damaged_files` are ignored. For a matching live file, invalid non-data key ranges trigger panic mark and panic. If too many damaged files are tracked, it also panics. Otherwise, while holding `StoreMeta`, the runner calls `update_overlap_damaged_ranges`; overlapping files are tracked and reported to PD through store meta state, while non-overlapping files are deleted with `delete_files_in_range(..., include_end = true)`.

Timer `on_timeout` clones and filters the damaged file list. Each file exceeding `max_hang_duration` causes panic mark and panic. Remaining files are rechecked for region overlap; files that no longer overlap are deleted and removed from the gauge.

## State and Persistence Behavior
The runner mutates in-memory `damaged_files`, Prometheus metrics, and raftstore `StoreMeta` damaged-region tracking. It can delete RocksDB SST files through `delete_files_in_range`, which is persistent/destructive. On fatal conditions it calls `set_panic_mark` before panicking.

## Dependencies and Integration Points
It integrates `engine_rocks::RocksEngine`, RocksDB live-file metadata, raftstore `StoreMeta`, `tikv_util::worker` scheduling/timer traits, TiKV data-key validation, failpoint `sst_recovery_before_delete_files`, and helper metrics. PD reporting is implied by `StoreMeta` damaged-region IDs.

## Risks and Edge Cases
The code only supports data-key ranges; raft/meta/keyspace files outside that shape panic. It tracks at most two damaged files to avoid broad data loss scenarios. Deletion while holding `StoreMeta` intentionally prevents peers from being re-added, but can block metadata operations. `delete_files_in_range` cannot delete L0 files, so `must_file_not_exist` panics if a file remains. `unwrap` on deletion errors means unexpected RocksDB failures panic.

## Test Signals
`test_sst_recovery_runner_check_overlap` creates an SST with range `z2..z7`, constructs overlapping region ranges, schedules recovery, and verifies the expected damaged region IDs are marked. Additional coverage should include no-overlap deletion, L0 undeletable file panic, timeout panic, duplicate scheduling, invalid key ranges, and max damaged-file enforcement.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks_helper/src/sst_recovery.rs -->
