# sources/object-store/garage/src/model/s3/lifecycle_worker.rs

## Purpose
This file implements the background worker that applies S3 lifecycle rules: expiring current objects by inserting delete markers and aborting stale incomplete multipart uploads.

## Important APIs, types, and functions
`LifecycleWorkerPersisted` stores `last_completed`. `LifecycleWorker` owns `Garage`, current `State`, and persister. `State` is `Completed(date)` or `Running` with scan position, counters, and cached last bucket. `register_bg_vars` exposes last completed date. Worker methods implement `name`, `status`, `work`, and `wait_for_work`. `process_object`, `check_size_filter`, `midnight_ts`, `next_date`, and `today` implement lifecycle decisions.

## Control flow
On startup, the worker compares persisted completion date to today and either idles or starts a scan. `work` processes up to 100 object-table rows per run using raw DB cursor position. It skips buckets without enabled lifecycle rules, reusing `last_bucket` for consecutive objects. For expiration rules, it finds the latest data version, checks prefix, size, and date filters, then queues an object update containing a new delete marker. For abort rules, it queues aborted states for old uploading versions. When the scan ends, it persists `last_completed` and becomes idle until the next local/UTC midnight.

## State and persistence behavior
Worker progress is in memory during a day; only the completed date is persisted. Object expirations and MPU aborts persist as object-table updates, which trigger normal object/version/MPU cascades. The worker uses either local timezone or UTC based on config.

## Dependencies and integration points
It depends on background worker traits, chrono, persister, bucket lifecycle config, object table, Garage DB transactions, and object-table update hooks. `Garage::spawn_workers` starts it and registers bg variables.

## Risks and edge cases
If Garage restarts mid-scan, the day restarts from the beginning because only completed date is persisted. Lifecycle `AtDate` strings are validated at processing time; invalid persisted dates log warnings. The worker inserts delete markers rather than deleting all versions, matching versioning semantics but requiring upper layers to interpret latest delete marker. `status` has a formatting typo in `"Multipart uploads aborted: { }"`. Timezone midnights can be ambiguous for local DST and use `.single().expect`.

## Test signals
No direct tests here. Useful tests should cover date math, prefix/size filters, expiration delete-marker insertion, MPU abort insertion, restart behavior, invalid lifecycle dates, local timezone behavior, and skip-bucket cursor advancement.
