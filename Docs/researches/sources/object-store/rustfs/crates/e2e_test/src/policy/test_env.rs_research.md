# sources/object-store/rustfs/crates/e2e_test/src/policy/test_env.rs

Purpose: lightweight environment wrapper for policy variable tests that connect to an already-running RustFS server and intentionally do not stop it on drop.

Important APIs/types/functions: `PolicyTestEnvironment` stores `temp_dir`, `address`, `url`, and admin credentials. `with_address` creates a unique temp directory and endpoint URL. `create_s3_client` builds a path-style AWS S3 client with supplied credentials, us-east-1, and the environment endpoint. `wait_for_server_ready` polls TCP connectivity for up to 30 seconds. `Drop` removes only the temp directory.

Control flow: policy tests or the runner instantiate `with_address("127.0.0.1:9000")`, optionally wait for readiness, then create admin or user S3 clients. Drop cleanup is local filesystem only.

State and persistence behavior: no server process ownership. Admin users, policies, and buckets live on the external RustFS instance and must be cleaned by tests. The temp directory is unique per environment and deleted best-effort on drop.

Dependencies and integration points: uses `aws_sdk_s3` config/credentials, `TcpStream` readiness checks, Tokio sleep, `uuid` temp directory naming, and tracing. It is consumed by `policy_variables_test.rs` and `test_runner.rs`.

Risks: TCP readiness only proves the port accepts connections, not that admin/S3 APIs are ready. Default admin credentials are hardcoded. Drop uses blocking std filesystem removal from a test context. Because the environment does not own the server, stale global state can affect results.

Test signals: indirect; supports ignored policy E2E tests and the ignored critical-suite runner.
