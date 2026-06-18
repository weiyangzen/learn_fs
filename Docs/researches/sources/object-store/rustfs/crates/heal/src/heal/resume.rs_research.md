<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/resume.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/resume.rs

## Purpose

`resume.rs` implements disk-backed resume and checkpoint state for heal tasks, especially erasure-set healing. It serializes JSON files into the RustFS meta bucket on a `DiskStore`, provides managers for updating state safely behind async locks, and offers utilities to discover and clean resumable tasks.

## Important APIs, types, and functions

- Constants define file suffixes: `ahm_resume_state.json`, `ahm_progress.json`, and `ahm_checkpoint.json`.
- `path_to_str` validates UTF-8 paths before disk API calls.
- `ResumeState` stores task identity/type, set disk id, timestamps, completion flag, object counters, current bucket/object, completed/pending buckets, error string, retry count, and max retries.
- `ResumeState` methods update progress, current item, bucket completion, completion flag, error, retry count, retry eligibility, progress percentage, and success rate.
- `ResumeManager` owns a `DiskStore` and `Arc<RwLock<ResumeState>>`.
- `ResumeManager::new`, `load_from_disk`, `has_resume_state`, `get_state`, update methods, `cleanup`, `save_state`, and `read_state_file` are the state file API.
- `ResumeCheckpoint` stores task id, checkpoint timestamp, current bucket/object indexes, processed objects, failed objects, and skipped objects.
- `CheckpointManager` mirrors `ResumeManager` for checkpoint creation/loading/existence, position/object-list updates, cleanup, save, and read.
- `ResumeUtils` generates UUID task ids, checks resumability, lists resume files, and cleans expired states.

## Control flow

Creating a `ResumeManager` builds a fresh `ResumeState`, then attempts to save it. Initial save failures are logged as warnings but do not fail construction. Subsequent update methods modify the in-memory state under a write lock, drop the lock, then serialize and write the whole JSON state file. Loading reads the state file and deserializes it.

`save_state` writes `{task_id}_ahm_resume_state.json` under `BUCKET_META_PREFIX` in `RUSTFS_META_BUCKET`. If the disk reports `UnformattedDisk`, the save is skipped and returns success, allowing healing of unformatted disks to proceed without resume persistence on that disk. Other write errors are converted to `TaskExecutionFailed`.

`CheckpointManager` follows the same pattern but writes `{task_id}_ahm_checkpoint.json`. Unlike resume state save, checkpoint save does not special-case unformatted disks. Processed/failed/skipped object additions deduplicate by linear `Vec::contains`.

Cleanup deletes state, progress, and checkpoint files for `ResumeManager`, and checkpoint file for `CheckpointManager`, ignoring delete errors. `ResumeUtils::get_resumable_tasks` lists `BUCKET_META_PREFIX`, filters entries ending in `_ahm_resume_state.json`, strips the suffix, and returns non-empty task ids. Expired cleanup loads each task and removes states whose `last_update` age exceeds a caller-supplied hour threshold.

## State and persistence behavior

Persistence is JSON written through `DiskStore::write_all` into the metadata bucket. State writes are whole-file replacements. Resume and checkpoint managers keep an in-memory copy under `RwLock` and persist after each mutation. `RESUME_PROGRESS_FILE` is only cleaned here; this file does not create or update a separate progress JSON file.

Timestamps are Unix seconds. `ResumeState::new` initializes `pending_buckets` from the caller and leaves `total_objects` at zero. `completed_buckets` and checkpoint object lists can grow for the lifetime of a task and are stored as arrays in JSON.

## Dependencies and integration points

This file integrates with `rustfs_ecstore::disk::{DiskAPI, DiskStore, RUSTFS_META_BUCKET, BUCKET_META_PREFIX}` and `DiskError`, uses crate `Error`/`Result`, serializes through `serde_json`, and uses `uuid` for task ids. `ErasureSetHealer` uses `ResumeManager`, `CheckpointManager`, and `ResumeUtils` to resume work for a set disk id. Tests use local disk construction and temp directories.

## Risks and edge cases

- Initial save failures are warnings, so callers can believe resume is enabled even if the first state/checkpoint was not persisted.
- Resume state save ignores `UnformattedDisk`, but checkpoint save does not; new checkpoint creation logs initial failure and continues, while later checkpoint updates can fail the heal.
- Whole-file JSON writes after every object-list update can become expensive for large buckets because processed/failed/skipped vectors grow without compaction.
- Object names in checkpoint lists are not bucket-qualified.
- `cleanup_expired_states` computes `current_time - state.last_update` directly; if a corrupt/future timestamp appears, unsigned subtraction can panic in debug or underflow semantics depending on build behavior.
- `ResumeUtils::get_resumable_tasks` depends on `list_dir` returning names in a format compatible with suffix stripping; callers should verify whether returned entries include the prefix.
- `RESUME_PROGRESS_FILE` is deleted but not otherwise managed, suggesting either planned functionality or compatibility with older code.

## Test signals

Tests cover resume state creation, progress math, bucket completion bookkeeping, UUID generation, and integration listing of resumable task files while ignoring checkpoint/progress/empty-id files. Additional tests should cover load/save round trips, unformatted-disk save behavior, checkpoint updates and cleanup, expired cleanup with future timestamps, and large checkpoint performance.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/resume.rs -->
