# sources/object-store/rustfs/crates/e2e_test/src/protocols/test_env.rs

## Purpose

This file defines the minimal protocol-test environment shared by FTPS, SFTP, and WebDAV e2e tests. It owns a unique temporary data directory, exposes default credentials, and provides TCP port readiness polling without owning server shutdown.

## Important APIs, Types, And Functions

`DEFAULT_ACCESS_KEY` and `DEFAULT_SECRET_KEY` are both `rustfsadmin` and are shared by protocol tests and SFTP/S3 helper clients.

`ProtocolTestEnvironment { temp_dir: String }` creates a directory under the system temp directory named with a UUID. `new()` creates that directory and converts the path to UTF-8, returning an error if conversion fails.

`wait_for_port_ready(port, max_attempts)` tries to connect to `127.0.0.1:<port>` once per second until success or the attempt budget is exhausted. It logs success and returns an error naming the timeout when the server never listens.

`Drop` removes `temp_dir` and logs a warning if cleanup fails. It deliberately does not stop any server process.

## Control Flow

Tests call `ProtocolTestEnvironment::new()` before generating host keys or spawning RustFS. The temp directory is passed as the RustFS data path. After the process is started, tests call `wait_for_port_ready` for the protocol listener before opening protocol clients. Server shutdown is handled outside this struct by direct child process handling or `ServerProcess`.

## State And Persistence Behavior

The environment creates a real temporary filesystem directory and deletes it on drop. RustFS uses that directory for its backend state during e2e tests, so bucket and object persistence lasts only for the environment lifetime. Because this struct does not own child processes, dropping it before killing RustFS could remove data while a server is still running; existing tests keep environment and server process in the same scope and kill the child before leaving.

## Dependencies And Integration Points

The file uses `uuid`, `std::net::TcpStream`, `tokio::time::sleep`, and `tracing`. It is consumed by SFTP core/compliance and WebDAV tests. The credentials are also used in `sftp_helpers.rs` and WebDAV basic auth helpers.

## Risks And Edge Cases

Readiness is TCP-level only. Some tests also need service-level readiness such as S3 `ListBuckets`, so they must call additional helpers. `temp_dir` is stored as `String`, so non-UTF-8 temp paths are rejected. Cleanup is best effort and can fail if a child process still holds files.

## Test Signals

No direct tests exist here. Its behavior is exercised indirectly by every protocol e2e test that creates a temp environment or waits for a spawned listener.
