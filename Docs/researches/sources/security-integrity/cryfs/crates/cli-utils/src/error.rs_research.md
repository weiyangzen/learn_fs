## sources/security-integrity/cryfs/crates/cli-utils/src/error.rs

Purpose: defines structured CLI errors with stable process exit-code mapping and helper traits for converting lower-level errors into `CliError`.

Important APIs and types: `CliError` stores `CliErrorKind` and an `Arc<anyhow::Error>` and displays the inner error. `CliResultExt` maps `Result<T, anyhow::Error>` and `Result<T, Arc<anyhow::Error>>` to a fixed kind. `CliResultExtFn` maps arbitrary error types through a function. `CliErrorKind` enumerates success, argument/config/password/version/path/integrity/filesystem errors.

Control flow and state: `CliErrorKind::exit_code` maps each kind to a fixed `ExitCode`: success is 0, unspecified is 1, and domain-specific errors occupy 10 through 28.

Dependencies and integration: uses `derive_more::Display`, `serde` derives, `anyhow`, and standard `Error`. `Application::run` prints `CliError` and returns `kind.exit_code()`.

Risks and test signals: comments note missing tests for exact shell exit codes and parity with old C++ behavior. Stable numeric codes are operationally important for scripts; adding or changing variants requires care to preserve compatibility.
