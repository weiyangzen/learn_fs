# sources/security-integrity/cryfs/crates/check/src/lib.rs

Purpose: This is the library root for `cryfs-check`. It forbids unsafe code, declares internal modules, and reexports the public API used by the binary and tests.

Important APIs and flow: It exports `RecoverCli`, `check_filesystem`, concrete corruption errors, `CorruptedError`, and node/blob info/reference types. Internal modules include args, cli, checks, console, error, node_info, assertion, runner, and task_queue. It asserts Cargo version equals git version through `cryfs_version`.

State and persistence: The root owns no state. It controls API visibility and keeps runner/check internals private while exposing diagnostic data types.

Dependencies and integration: The binary imports `RecoverCli` from here. Integration tests import errors and reference model types from the crate to build exact expected results.

Risks and test signals: Public reexports make diagnostic type shapes part of the crate contract. The TODO for missing docs suggests API documentation is incomplete for external callers.
