# sources/security-integrity/cryfs/crates/check/src/bin/cryfs-check.rs

Purpose: This is the binary entrypoint for the `cryfs-check` executable.

Important APIs and flow: `main` returns `ExitCode` and delegates all parsing, setup, logging, and error handling to `cryfs_cli_utils::run::<RecoverCli>()`.

State and persistence: The file has no state. Runtime behavior is owned by `RecoverCli`.

Dependencies and integration: It imports `cryfs_check::RecoverCli`, which is exported by the library crate. This keeps the binary thin and testable logic in `lib.rs` modules.

Risks and test signals: There are no local tests. A TODO notes integration tests for the binary path, while existing crate integration tests call checker helpers through fixtures.
