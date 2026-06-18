# sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_compliance_tests.rs

## Purpose

This file is the implementation body for RustFS SFTP compliance regression coverage. It contains one module per CMPTST case, plus shared process-spawn, fixture, stream-wrapper, log-capture, hashing, and socket-state helpers. The companion dispatcher `sftp_compliance.rs` wires these modules into three public suite entries: shared read-write compliance, read-only compliance, and standalone server regressions. The file is intentionally broad: it tests SFTP protocol semantics, S3-backed persistence behavior, pathological client transport patterns, large object reads, pipelining, read-cache modes, and metadata preservation across multipart uploads.

The top-level module documentation is a load-bearing case index. It maps CMPTST-01 through CMPTST-34 to concrete regression properties. CMPTST-01..14 use a shared read-write SFTP server, CMPTST-15..23 use a read-only SFTP server seeded through S3, and CMPTST-24..33 are standalone process-level regressions. CMPTST-34 is implemented here but invoked by the shared read-write dispatcher after CMPTST-14 because it needs both the same SFTP session and an S3 client against the same process.

## Important APIs, Types, And Functions

`spawn_compliance_rustfs(sftp_address, s3_address, read_only)` is the externally used spawn helper. It creates a `ProtocolTestEnvironment`, generates an ed25519 host key, starts the RustFS binary with `ENV_SFTP_ENABLE`, `ENV_SFTP_ADDRESS`, `ENV_SFTP_HOST_KEY_DIR`, `ENV_SFTP_READ_ONLY`, `ENV_SFTP_PART_SIZE`, and `ENV_RUSTFS_ADDRESS`, then returns the environment plus `ServerProcess`.

`spawn_pipelining_rustfs` and `spawn_pipelining_rustfs_with_extras` are local variants for long-running or diagnostic standalone cases. They disable the console listener, set bounded SFTP protocol logging via `RUSTFS_OBS_LOGGER_LEVEL` and `RUST_LOG`, pipe stdout for diagnostic capture, and optionally inject extra environment variables such as `ENV_SFTP_READ_CACHE_WINDOW_BYTES`.

Fixture helpers include `seed_pipelining_fixture`, `seed_large_via_multipart`, `calculate_pattern_sha256`, and `streaming_sha256_download`. Together they support deterministic byte-pattern seeding through S3 multipart upload and bounded-memory SHA256 verification through SFTP. This matters for multi-GiB reads because the tests do not materialize the entire expected payload in memory.

`capture_server_stdout` keeps a bounded in-memory tail of spawned server stdout for failure dumps. `SessionCounters` and `watch_session_lifecycle_events` scrape "SFTP session task entered/finished/panicked" log lines for lifecycle assertions in socket-regression cases. On Linux, `count_close_wait_on_port` shells out to `ss -tn state CLOSE-WAIT` and returns a best-effort socket count for a specific local port.

The case modules expose descriptive `pub(crate) async fn run_*` entries. Semantics cases cover medium and zero-byte round trips, rm/rmdir rejection, path traversal and `/..` handling, cross-bucket rename, paths with spaces, readlink rejection, SETSTAT/FSETSTAT behavior, same-path rename, implicit directories, WinSCP write-handle FSETSTAT, read-only mutation rejection, and read-only reads. Transport and performance cases define custom stream wrappers: `HalfClosableStream`, `WedgeStream`, and `PausableStream` implement `AsyncRead`/`AsyncWrite` around split `TcpStream` halves and atomics to simulate half-closed, wedged, or paused-drain clients while keeping the russh client task alive.

## Control Flow

The normal read-write compliance flow is: spawn RustFS, wait for SFTP port readiness, connect with `connect_sftp_to`, run CMPTST-01..14 over one SFTP session, create an S3 client to the same process, run CMPTST-34, disconnect, then `kill_and_wait` the server. The read-only flow is similar but starts with `read_only=true`, seeds a bucket/object through S3, then runs CMPTST-15..23 to prove SFTP mutations fail while listing and reading still work.

Standalone flows each own their process lifecycle because they depend on dedicated ports and environment. CMPTST-24 and CMPTST-25 create multiple custom-stream russh sessions, force FIN/CLOSE_WAIT or server-channel wedge states, wait for watchdog or idle-timeout behavior, tickle the accept loop with short TCP connects so task completions are drained, then assert task-counter balance and zero CLOSE_WAIT entries when `ss` is available. CMPTST-26 is the inverse: it keeps a healthy idle session alive past the fast-kill threshold and asserts it was not false-killed. CMPTST-27 seeds a multi-GiB fixture and downloads it concurrently on four SFTP sessions under a one-hour no-progress deadline. CMPTST-28 runs a 5 MiB download while parallel sessions issue hundreds of metadata and readdir operations. CMPTST-29 opens many handles and issues 10,000 reads past EOF, expecting fast EOF responses. CMPTST-30 measures metadata handler latency under pipelined load but is ignored by default. CMPTST-31 pauses client-side reads mid-transfer, resumes, and verifies byte-exact completion. CMPTST-32 and CMPTST-33 share `run_read_cache_byte_correctness` with cache window enabled and disabled.

## State And Persistence Behavior

All persistent storage under test is the RustFS data directory created by `ProtocolTestEnvironment` and the S3 object store surfaced by the spawned RustFS process. Tests create buckets and objects through SFTP and S3, then validate persistence through the opposite protocol or through metadata APIs. Directory state is modeled through buckets, object prefixes, and RustFS directory markers such as `__XLDIR__` in related core tests; this file focuses on compliance behavior such as implicit directory listing and non-empty rmdir rejection.

Multipart state is important in `seed_large_via_multipart` and CMPTST-34. Large fixtures are written part by part with S3 multipart APIs and completed only after all parts have ETags. CMPTST-34 specifically asserts that SFTP `OPEN` attributes survive the SFTP buffering-to-streaming multipart path and become object metadata visible through S3 `HeadObject`.

Process state is guarded with `ServerProcess`, which kills children even on panic paths. Temp directories are cleaned by `ProtocolTestEnvironment` drop. Several tests intentionally hold russh handles, SFTP sessions, channels, and stream controls in vectors so client sockets remain in the intended pathological state until the server-side assertion window completes.

## Dependencies And Integration Points

Major dependencies are `russh`, `russh_sftp`, `tokio`, `aws_sdk_s3`, `sha2`, `futures::stream::FuturesUnordered`, `anyhow`, and RustFS config constants from `rustfs_config`. The file relies on local helpers from `sftp_helpers.rs` for host-key generation, SFTP connection, S3 client construction, and full-file reads. It uses `ProtocolTestEnvironment` from `test_env.rs` for temp directories and TCP readiness polling.

The public integration point is indirect: `sftp_compliance.rs` imports the `cmptst_*` modules and `spawn_compliance_rustfs`, then `test_runner.rs` schedules those public suite functions under the `sftp` feature. Linux-specific cases are guarded with `#[cfg(target_os = "linux")]`; CMPTST-30 is `#[ignore]`, and CMPTST-31 has a direct `#[tokio::test]` but is intentionally omitted from the default standalone dispatcher for runtime cost.

## Risks And Edge Cases

The file is highly integration-heavy and port-bound. Fixed local ports from 9024 through 9035 and S3 ports around 9300 can conflict with leaked servers or local development processes. Several cases have long waits or large fixtures: CMPTST-25 and CMPTST-26 wait 90 seconds, CMPTST-27 defaults to 5 GiB, and CMPTST-31 seeds 200 MiB and pauses 25 seconds. These are strong regression signals but expensive in CI.

Socket-state assertions are platform-sensitive. `count_close_wait_on_port` skips when `ss` is unavailable, so Linux without `ss` loses part of the signal. Log-scraped counters depend on exact server log messages. If logging text changes, lifecycle tests may fail or undercount despite correct runtime behavior.

The custom stream wrappers intentionally return `Poll::Pending` in unusual situations. That makes them useful for reproducing real client pathologies, but small russh behavior changes can alter how reliably they hold sockets in the desired state. The read-cache e2e tests assert byte correctness only; backend request-count behavior is left to lower-level unit tests.

## Test Signals

This file is itself a dense test source. Signals include SHA256 equality, byte-count equality, S3 `HeadObject` metadata checks, expected errors for unsupported or forbidden SFTP operations, directory listing contents, watchdog lifecycle counter balance, CLOSE_WAIT counts, timeout-enforced completion, EOF semantics, and ignored latency ceiling checks. The small unit test `cmptst29_eof_status_matches_protocol_constant` pins `StatusCode::Eof as u32 == 1` so dependency changes in `russh_sftp` surface before the high-volume EOF regression runs.
