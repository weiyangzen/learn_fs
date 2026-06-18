# sources/object-store/rustfs/crates/e2e_test/src/common.rs

## Purpose
This is the shared support module for e2e tests. It manages RustFS server and cluster lifecycles, builds S3 and HTTP clients, finds/builds the RustFS binary, signs admin calls through awscurl, normalizes build-feature requests, initializes logging, and cleans temporary test storage.

## Important APIs, Types, and Functions
Constants define default credentials and a common bucket. `build_test_s3_config`, `local_http_client`, and S3 client factory methods configure path-style AWS SDK clients. `workspace_root`, `rustfs_binary_path`, `rustfs_binary_path_with_features`, feature normalization, source freshness checks, and binary feature stamps coordinate binary reuse/builds. `RustFSTestEnvironment` manages one server. `RustFSTestClusterEnvironment` manages multiple nodes and cluster volumes. Awscurl helpers cover GET, POST, PUT, DELETE, and STS form posts.

## Control Flow
Single-server startup optionally kills existing matching processes, builds command args, spawns the RustFS binary, and waits for readiness by requiring both TCP connectivity and successful `list_buckets`. Cluster startup allocates per-node ports and directories, builds a shared `RUSTFS_VOLUMES` string, spawns each node, waits for TCP readiness, then waits for S3 readiness on each node. Drops stop child processes and remove temp directories.

## State and Persistence
The module creates temporary directories under `/tmp`, stores child process handles, records cluster node address/data-dir state, writes binary feature stamp files next to the RustFS binary, and can build the RustFS binary into workspace `target`. Awscurl helpers do not persist state themselves.

## Dependencies and Integration Points
It integrates `aws-sdk-s3`, `aws-smithy-http-client`, `reqwest`, `tokio`, `tracing`, `uuid`, `walkdir`, local RustFS binaries, environment variables, and external `awscurl`. Almost every requested e2e file depends on this module.

## Risks and Edge Cases
`cleanup_existing_processes` uses `pkill -f` against address and temp-dir patterns, which is powerful and Unix-specific. Binary freshness scanning can be expensive over large workspaces. Readiness loops rely on `list_buckets`, so auth or routing regressions surface as startup failures. Feature stamp correctness matters when tests require optional protocol features.

## Test Signals
Inline unit tests cover feature normalization, `full` feature matching, and normalized binary feature-stamp matching. All e2e tests indirectly exercise server startup, readiness, client creation, process cleanup, and temp-dir cleanup.
