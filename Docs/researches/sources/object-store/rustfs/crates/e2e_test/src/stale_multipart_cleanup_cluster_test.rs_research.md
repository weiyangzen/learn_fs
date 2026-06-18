# sources/object-store/rustfs/crates/e2e_test/src/stale_multipart_cleanup_cluster_test.rs

Purpose: cluster e2e regression test proving stale incomplete multipart uploads are removed across all RustFS nodes.

Important APIs and functions: `list_parts_reports_missing_upload` and `complete_reports_missing_upload` both probe an upload ID and normalize `NoSuchUpload` service errors to `true`. `wait_for_cleanup_on_all_nodes` loops for up to 30 seconds, requiring every client to report missing upload for both list-parts and complete-multipart.

Control flow: the test starts a four-node `RustFSTestClusterEnvironment`, sets `RUSTFS_API_STALE_UPLOADS_EXPIRY=5s` and `RUSTFS_API_STALE_UPLOADS_CLEANUP_INTERVAL=1s`, creates a bucket, starts a multipart upload through node 0, uploads part 1 through node 1, verifies visibility through node 2, then waits until every node observes cleanup.

State and persistence: the multipart upload metadata and part data are intentionally left incomplete so background cleanup can remove them. The test observes distributed metadata convergence, not just local disk deletion.

Dependencies and integration points: uses AWS SDK multipart APIs, cluster harness clients, `tokio::time::sleep`, `uuid` for unique object keys, and `serial_test`.

Risks: timing based on real background intervals can be flaky under slow CI. The helper treats only exact `NoSuchUpload` as success; any alternate S3-compatible error mapping fails the test.

Test signals: confirms stale upload expiration configuration, background cleanup scheduling, and cluster-wide propagation for incomplete multipart state.
