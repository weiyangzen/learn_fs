# sources/object-store/rustfs/crates/e2e_test/src/admin_timeout_regression_test.rs

## Purpose
This e2e regression test verifies that a single slow or suspended peer in a four-node cluster does not cause admin `/info` or `/storageinfo` endpoints to synthesize offline disks or offline servers. It targets an issue where one admin timeout could incorrectly mark healthy cluster state as degraded.

## Important APIs, Types, and Functions
`signed_admin_get` manually signs admin GET requests with `rustfs_signer::sign_v4` and `UNSIGNED_PAYLOAD`. `fetch_info` and `fetch_storage_info` parse admin JSON into `rustfs_madmin::InfoMessage` and `StorageInfo`. `offline_server_count` counts servers whose state is `ITEM_OFFLINE`. The test uses `RustFSTestClusterEnvironment` for cluster lifecycle and AWS S3 SDK for an object put/get during the peer suspension window.

## Control Flow
The test starts a four-node cluster, creates a bucket, verifies warm admin state has zero offline disks, sends `SIGSTOP` to node 1, schedules `SIGCONT` after six seconds, and concurrently fetches admin info, storage info, and writes an object through node 0 under a 20-second timeout. After the peer resumes, it asserts admin responses showed no offline state and the object remains readable.

## State and Persistence
State includes temporary cluster data directories, child RustFS processes, one test bucket, and one object key. Process suspension is OS-level state controlled by `kill -STOP` and `kill -CONT`.

## Dependencies and Integration Points
The test integrates admin HTTP endpoints, RustFS distributed storage state, process management, SigV4 signing, and S3 object I/O. It is registered from `e2e_test/src/lib.rs` under `#[cfg(test)]`.

## Risks and Edge Cases
The test is Linux/Unix-specific because it shells out to `kill` with signals. Timing can be sensitive on slow machines, although generous admin and readiness timeouts help. It asserts a single suspended node should not become offline during the narrow admin timeout window, not long-term node failure behavior.

## Test Signals
Positive signals are zero offline disks before suspension, zero offline disks and zero offline servers during suspension, successful concurrent `PutObject`, zero offline disks after resume, and exact object body readback.
