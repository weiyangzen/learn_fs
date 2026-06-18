## sources/security-integrity/encfs/Taskfile.yml

Purpose: Task runner definitions for common EncFS development workflows: build, release build, macOS cross-target build, unit/integration tests, live tests, formatting, clippy, coverage, fuzzing, and cleanup.

Important APIs and functions: Taskfile version 3, variables `CARGO`, `LIVE_TIMEOUT_SECS`, `MACOS_TARGET`, tasks `build`, `build-release`, `build-osx`, `test`, `test-live`, `fmt`, `fmt-check`, `clippy`, `coverage`, `fuzz`, `fuzz-build`, `clean`. Control flow is command execution; live tests set `ENCFS_LIVE_TESTS=1` and `ENCFS_LIVE_MOUNT_TIMEOUT_SECS`.

State and persistence: Cargo build outputs, coverage outputs, fuzz artifacts. Dependencies include go-task, cargo-nextest, cargo-tarpaulin, cargo-fuzz/nightly for optional tasks, and FUSE for live tests. Integration provides local parity with CI plus fuzz entry points. Risks are optional tool availability and live test privilege/kernel requirements.
