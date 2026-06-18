<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/erasure_healer.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/erasure_healer.rs

## Purpose

`erasure_healer.rs` implements resume-aware erasure-set healing. It scans configured buckets, pages through objects, checks or heals each object using the `HealStorageAPI`, records progress/checkpoints to disk-backed resume managers, and cleans up resume state after successful completion. It is the worker-side implementation for `HealType::ErasureSet` tasks.

## Important APIs, types, and functions

- `ErasureSetHealer` holds the storage API, shared `HealProgress`, cancellation token, resume/checkpoint disk, and `HealOpts`.
- `page_parallel_enabled`, `heal_page_object_concurrency`, `effective_heal_page_object_concurrency`, and `effective_heal_page_object_concurrency_for_scan_mode` read configuration and force deep scans to serial object processing.
- `heal_erasure_set` is the public entry point. It creates or resumes a task id, initializes resume/checkpoint managers, runs healing, and cleans durable resume files on success.
- `get_or_create_task_id` scans disk resume state for a matching `set_disk_id`, otherwise creates `{set_disk_id}_{uuid}`.
- `initialize_resume_state` loads existing resume/checkpoint files or creates new `ResumeManager` and `CheckpointManager` instances.
- `execute_heal_with_resume` initializes in-memory progress from resume state, continues from checkpoint bucket/object indexes, updates resume counters, handles cancellation, and marks completion.
- `heal_bucket_with_resume` pages object listings, skips already processed/skipped checkpoint entries, runs per-page object heal futures with a semaphore, updates checkpoint object sets and positions, and records success/failure/skip counters.
- `initialize_progress` maps persisted resume counters into `HealProgress`.
- Dead-code helpers `heal_buckets_concurrently`, `heal_single_bucket`, `heal_objects_concurrently`, and `process_results` show an older non-resume concurrent implementation retained for reference/tests.

## Control flow

Healing starts by selecting a resumable task for the same set disk id when possible. If no state exists, a new resume state and checkpoint are written to the disk's meta bucket. `execute_heal_with_resume` clones the saved resume state and checkpoint, initializes counters from it, and iterates buckets from `current_bucket_index`, skipping buckets already marked complete.

For each bucket, `heal_bucket_with_resume` verifies the bucket exists, then repeatedly calls `list_objects_for_heal_page`. For each page it records a `global_obj_idx`, skips objects before `current_object_index`, and also skips objects already recorded as processed or skipped in the checkpoint. Each remaining object is healed in a future guarded by a page semaphore. Deep scans call `heal_object` directly and treat not-found errors as a non-failing skip/ok. Normal scans first call `object_exists`, then heal existing objects. `TransientSkip` is counted separately and checkpointed as skipped.

When futures complete, successes and missing-as-ok objects are added to processed checkpoint state; transient skips are added to skipped; other failures are added to failed. The processed counter is incremented for every completed future. The checkpoint position is written after each page and periodically inside large pages. Cancellation returns `TaskCancelled` and resets the page concurrency gauge to zero.

After each bucket, resume progress is saved and successful bucket completion updates `completed_buckets`. Bucket-level errors are logged and do not stop later buckets. At the end the resume state is marked completed, and the top-level `heal_erasure_set` removes resume/checkpoint files only when the overall result is `Ok`.

## State and persistence behavior

Durable state is delegated to `ResumeManager` and `CheckpointManager`, which write JSON under the RustFS meta bucket on the selected `DiskStore`. Resume state stores task counters, current bucket/object, completed/pending buckets, set id, retry metadata, and completion. Checkpoint state stores bucket/object indexes plus processed/failed/skipped object name lists.

In-memory progress is a best-effort view backed by `Arc<RwLock<HealProgress>>`; it is initialized from resume state but not updated for every object in this file except through resume counters. Metrics include `rustfs_heal_page_concurrency_current` with a set label.

## Dependencies and integration points

The implementation depends on `HealStorageAPI` for bucket lookup, paged listing, existence checks, and object healing. It depends on `resume.rs` for persistent state and on `progress.rs` for user-visible progress. Configuration comes from `rustfs_config` and `rustfs_utils`; scan mode and options come from `rustfs_common::heal_channel::HealOpts`. It uses `tokio_util::CancellationToken`, `tokio::Semaphore`, `FuturesUnordered`, `join_all`, metrics gauges, and structured `tracing`.

## Risks and edge cases

- Checkpoint object sets store object names without bucket qualification. Since checkpoints are per erasure-set task and processing is bucket-indexed, duplicate object names across buckets may cause unwanted skips if a later bucket contains the same object name.
- `checkpoint` is captured before iterating a page, so processed/skipped membership used for that page does not include updates made while the page is running.
- Periodic checkpoint updates inside a page use `page_resume_index`, not the completed object's global index. A crash mid-page may redo page work, which is safe but less precise.
- `ResumeState.total_objects` is never populated by this healer, so resume progress percentage based on total objects remains zero unless another component updates it.
- Non-deep scans skip missing objects as successful, while deep scans infer missing by string matching error messages containing `File not found` or `not found`.
- Bucket-level errors do not fail the overall task unless they surface outside the per-bucket `match`, so a task can complete with failed objects or failed buckets recorded only in counters/logs.
- Resume files are not cleaned on cancellation or failure, which is required for resume but may leave stale state until explicit expiration cleanup.

## Test signals

The file has focused tests for environment-driven page concurrency and the deep-scan serial override. Broader integration tests should exercise resume after crash/cancel, duplicate object names across buckets, transient skip behavior, checkpoint precision, bucket-list pagination without continuation token, normal versus deep scan missing-object handling, and gauge reset on early errors.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/erasure_healer.rs -->
