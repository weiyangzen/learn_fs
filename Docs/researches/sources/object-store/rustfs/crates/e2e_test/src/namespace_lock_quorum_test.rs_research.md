# sources/object-store/rustfs/crates/e2e_test/src/namespace_lock_quorum_test.rs

## Purpose

This Rust end-to-end test module is a cluster regression suite for namespace lock quorum behavior under concurrent same-key PUT overwrites. It verifies that RustFS does not surface false namespace-lock quorum failures during contention and that lock timeout/conflict failures are mapped to S3-compatible 503 `ServiceUnavailable` responses rather than 500 `InternalError`.

The tests start a four-node `RustFSTestClusterEnvironment`, create a bucket, seed an object, then issue simultaneous overwrites against the same key from multiple clients. They use a `tokio::sync::Barrier` to create real contention and classify results through AWS SDK service error metadata.

## Important APIs, Helpers, and Types

- `RustFSTestClusterEnvironment` from `crate::common` manages a multi-node RustFS test cluster, starts nodes, configures environment variables, creates buckets, and returns one S3 `Client` per node.
- `aws_sdk_s3::Client` is cloned into worker tasks and used for PUT/GET/DELETE operations.
- `bytes::Bytes` converts in-memory payloads into S3 request bodies.
- `tokio::sync::Barrier` synchronizes spawned writers so the PUT requests race on the same namespace lock.
- `serial_test::serial` keeps the cluster tests from running concurrently with other serial e2e tests.
- `tracing::{info, warn}` emits diagnostics for cluster setup, regression counts, and unexpected writer failures.
- `TestResult` is a local alias for `Result<(), Box<dyn std::error::Error + Send + Sync>>`.
- `put_object(client, payload, writer_id)` wraps `client.put_object().bucket(BUCKET).key(KEY).body(...).send()` and maps failures through `format_s3_error`.
- `format_s3_error(err, writer_id)` extracts service error code/message from `SdkError::ServiceError`; non-service SDK errors are formatted with debug output.

The constants under test are `BUCKET = "namespace-lock-quorum-bucket"` and `KEY = "thumb/79/concurrent-overwrite.jpg"`, giving both tests a shared path-like object key.

## Control Flow

`test_concurrent_cluster_overwrites_do_not_fail_namespace_lock_quorum`:

1. Initializes logging and creates a four-node cluster.
2. Sets `RUSTFS_OBJECT_LOCK_ACQUIRE_TIMEOUT` to `20`, intentionally focusing the regression on false quorum-loss errors rather than normal lock wait exhaustion.
3. Starts the cluster and creates the test bucket.
4. Creates clients for all cluster nodes and seeds an initial object.
5. Computes `writer_count = clients.len() * 2`, so a four-node cluster runs eight concurrent overwriters.
6. Builds a shared barrier and spawns one task per writer, rotating clients by `writer_id % clients.len()`.
7. Each task waits on the barrier, then overwrites the same key with a writer-specific payload.
8. The test joins all tasks, collects any service/SDK/join failures, logs them, and asserts that the failure list is empty.
9. It reads the final object and asserts that the body starts with `replacement payload from writer `, proving the final state is one of the successful concurrent writes.
10. It deletes the object before returning.

`test_concurrent_put_same_key_never_returns_500`:

1. Initializes logging and starts a four-node cluster.
2. Sets `RUSTFS_OBJECT_LOCK_ACQUIRE_TIMEOUT` to `3` to induce lock contention errors quickly.
3. Creates the bucket and seeds an initial object.
4. Runs `writer_count = clients.len() * 4`, so a four-node cluster runs sixteen concurrent PUTs.
5. Each spawned task waits on the barrier and then sends a direct `put_object`.
6. Results are classified into four atomic counters: successful writes, 503/service-unavailable errors, 500/internal errors, and unexpected errors.
7. Join failures count as unexpected errors.
8. The test logs total classified results and asserts that every writer was classified.
9. It asserts that unexpected errors are zero and, critically, that 500/InternalError count is zero.
10. It deletes the object before returning.

The two tests intentionally use different expectations: the first disallows all concurrent overwrite failures with a long timeout; the second allows successful writes or 503 contention failures but forbids 500s.

## State and Persistence Behavior

The tests mutate only S3-visible cluster state:

- A bucket is created in the test cluster.
- An initial object is written at the shared key.
- Multiple concurrent PUT operations overwrite that same key.
- The first test verifies final persisted body content after all overwrites complete.
- Both tests delete the key at the end.

No direct filesystem, lock-table, or quorum metadata is inspected. The namespace lock subsystem is validated through externally observable S3 results: absence of errors, final object contents, and service error codes under contention.

The cluster environment variable `RUSTFS_OBJECT_LOCK_ACQUIRE_TIMEOUT` is the key stateful configuration input. A longer timeout should let contended writers wait long enough to succeed, while a shorter timeout should surface lock contention as 503 without leaking internal 500s.

## Dependencies and Integration Points

This file integrates with:

- Cluster startup and lifecycle code in `RustFSTestClusterEnvironment`.
- RustFS namespace locking and distributed lock quorum logic.
- RustFS object PUT path for overwrites to an existing key.
- RustFS error mapping from namespace lock acquisition failures to S3 service errors.
- AWS SDK S3 service error metadata normalization.
- Tokio task scheduling and barriers to produce concurrent requests.

The comment above the second test documents the specific regression: `map_namespace_lock_error` previously wrapped lock timeout/conflict errors as a generic storage/IO error path, which fell through to `S3ErrorCode::InternalError` HTTP 500. This test locks in the expected mapping to 503 `ServiceUnavailable`.

## Risks and Edge Cases

- These are timing-sensitive concurrency tests. The barrier maximizes simultaneous start, but actual contention depends on runtime scheduling, machine load, and cluster performance.
- The first test sets a longer lock timeout to avoid ordinary contention failures, but a slow or overloaded environment could still make it flaky if PUTs exceed the timeout.
- The second test does not require at least one 503; if all writes succeed, the no-500 regression still passes. That is acceptable for error-mapping regression but weaker as a contention-generation signal.
- Both tests share fixed bucket/key constants and rely on serial execution plus fresh cluster state to avoid collisions.
- Error classification accepts both numeric and named codes for 500 and 503, which makes it robust to SDK/server metadata differences but assumes the service error metadata is populated.
- Cleanup only deletes the object, not the bucket; the cluster environment likely owns bucket cleanup when torn down.
- The tests do not verify which writer wins, only that the final body is from some writer payload.

## Test Signals

Strong signals:

- Multi-node cluster coverage with four nodes rather than a single embedded server.
- Same-key overwrite contention across multiple S3 clients.
- Barrier-synchronized start to increase lock collision probability.
- Explicit failure collection and logging for each writer in the no-failure quorum test.
- Atomic classification of success, 503, 500, and unexpected outcomes in the error-mapping test.
- Final object body readback proving successful overwrite persistence.

Coverage gaps:

- No assertion that 503 actually occurs in the second test, so a run with no lock contention still passes the no-500 check.
- No tests for concurrent deletes, multipart writes, copy operations, or cross-key lock independence.
- No direct validation of quorum repair/retry internals, only external S3 semantics.
- No bucket cleanup in the test body, relying on the cluster test harness for environment teardown.
