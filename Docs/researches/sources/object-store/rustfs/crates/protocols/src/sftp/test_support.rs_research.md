# sources/object-store/rustfs/crates/protocols/src/sftp/test_support.rs

## Purpose
`test_support.rs` provides shared `#[cfg(test)]` helpers for SFTP module tests. It lets tests instantiate `SftpDriver` and handle states around `DummyBackend` without real IAM or S3 services.

## Important APIs, Types, and Functions
`TEST_PART_SIZE` fixes a 5 MiB part size. `file_handle` builds a `HandleState::File` with an independent read-cache accumulator. `write_handle` builds a `HandleState::Write` around a supplied `WritePhase`. Driver builders include `build_driver`, `build_readonly_driver`, `build_driver_with_read_cache`, and `build_driver_with_timeout`. `capture_tracing_at` installs a temporary tracing subscriber backed by `CapturingWriter`.

## Control Flow
Driver builders construct test sessions with `Protocol::Sftp`, loopback `SessionDiag`, fresh handle maps, and default or supplied limits. `capture_tracing_at` registers a subscriber, rebuilds callsite interest cache, awaits the future, and returns output plus captured logs.

## State and Persistence Behavior
No production state is persisted. Test drivers and accumulators are fresh. `file_handle` uses an independent accumulator, so tests needing driver-level cache accounting must use real driver read paths.

## Dependencies and Integration Points
The module depends on SFTP constants, `SftpDriver`, `SessionDiag`, `ReadCache`, state types, `DummyBackend`, test sessions, `FileAttributes`, tracing, and tracing-subscriber. It is imported by tests across attrs, dir, driver, errors, paths, read, and write modules.

## Risks and Test Signals
The main risk is helper defaults drifting from production. Builders source defaults from constants to reduce drift. The tracing helper addresses flaky log assertions caused by tracing callsite interest caching.
