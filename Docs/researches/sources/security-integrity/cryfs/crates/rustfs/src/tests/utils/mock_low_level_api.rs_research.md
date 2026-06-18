# sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/mock_low_level_api.rs

Purpose: test-only mock coverage for the rustfs low-level async filesystem trait. It uses `mockall::mock!` to define `MockAsyncFilesystemLL`, implements every `AsyncFilesystemLL` operation, and gives integration tests a full FUSE-like backend surface without mounting a real filesystem implementation.

Important APIs/types/functions: `MockFilesystem` bundles the mock and an `Event` fired when `init` runs. `make_mock_filesystem()` installs default expectations for `init`, `destroy`, and `async_drop_impl`. The generated mock covers metadata, directory, file I/O, xattr, locking, block mapping, ioctl, allocation, lseek, copy range, and macOS-only operations. The file also manually implements `AsyncFilesystemLL` for `AsyncDropArc<MockAsyncFilesystemLL>` by forwarding every call through `Deref`.

Control flow: tests create a mock, configure expectations, wrap it as needed in `AsyncDropGuard`/`AsyncDropArc`, and pass it to backend adapters. Calls reach either mockall expectations directly or the `AsyncDropArc` forwarding layer. `init` triggers a one-shot event so test harnesses can wait until the filesystem is mounted/ready.

State/persistence: all state is in memory inside mockall expectation state and the readiness `Event`. No persistent data is written here. Async cleanup is enforced by the `AsyncDrop` expectation and by `AsyncDropArc` last-reference semantics.

Dependencies/integration: depends on `async_trait`, `mockall`, `cryfs_utils::async_drop`, `cryfs_utils::event::Event`, `PathComponent`, and rustfs common/low-level reply types. It is re-exported by the test utils module for filesystem-driver and runner tests.

Risks: this file mirrors a wide trait; trait signature drift will require synchronized updates in both the mock definition and the forwarding impl. The forwarding impl is repetitive and can hide missed platform-gated methods. Mock defaults expect exactly one init/destroy/drop; tests that intentionally exercise unusual lifetimes must override or account for those expectations.

Test signals: the file itself is test infrastructure. Its strongest signal is compile-time trait conformance against `AsyncFilesystemLL` plus mockall expectation failures in higher-level tests.
