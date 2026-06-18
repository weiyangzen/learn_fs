# sources/object-store/rustfs/crates/e2e_test/src/cluster_concurrency_test.rs

## Purpose
This file tests cluster-wide correctness for conditional `PutObject` requests using `If-None-Match: *`. It ensures concurrent writers to different nodes do not all win the same object creation race.

## Important APIs, Types, and Functions
`conditional_put` sends `put_object().if_none_match("*")` and maps `PreconditionFailed` service errors to `Ok(false)`. `run_race_iteration` deletes the object, confirms it is absent, synchronizes client tasks with a `tokio::sync::Barrier`, and counts successful writes. `cleanup_object` best-effort deletes between iterations.

## Control Flow
The race test starts a four-node cluster, creates a shared bucket, builds one S3 client per node, and runs five race iterations. Each iteration launches one task per client after a barrier and records if more than one write succeeded. The basic test verifies a first conditional put succeeds and a second on the same key fails with `PreconditionFailed`.

## State and Persistence
State includes a temporary four-node cluster, one bucket, and short-lived race-test object keys. The race test cleans each key before and after the iteration.

## Dependencies and Integration Points
The file integrates cluster process management, distributed namespace locking or quorum behavior, AWS S3 conditional write semantics, SDK error metadata, and async task scheduling.

## Risks and Edge Cases
Race tests can be timing-sensitive; the barrier increases contention but cannot prove every possible interleaving. The race suite treats any iteration error as failure to avoid hiding cluster readiness issues. Fixed bucket names require serial tests.

## Test Signals
The primary signal is zero race detections across five iterations, exactly one success per healthy race, zero iteration errors, and explicit `PreconditionFailed` on the second basic conditional put.
