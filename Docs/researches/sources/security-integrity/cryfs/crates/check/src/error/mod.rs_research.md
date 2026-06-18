# sources/security-integrity/cryfs/crates/check/src/error/mod.rs

Purpose: This module collects all concrete corruption errors and defines the checker's non-corruption operational error type.

Important APIs and flow: `CorruptedError` is an enum with transparent variants for node unreadable, missing, unreferenced, referenced multiple times, blob referenced multiple times, blob unreadable, and wrong parent pointer. `CheckError` currently contains `FilesystemModified { msg }`, representing analysis failure caused by concurrent filesystem changes rather than persistent corruption.

State and persistence: `CorruptedError` values are immutable diagnostics returned to callers. `CheckError` is transient and aborts a checker run.

Dependencies and integration: The module reexports concrete error structs and is reexported by `lib.rs`. Checks add concrete errors into `CheckResult`, and the runner propagates `CheckError` where observations become inconsistent.

Risks and test signals: The TODO asks whether node and blob multiple-reference errors should be unified. The separation between corruption and check failure is important: `FilesystemModified` should not be counted as a found corruption.
