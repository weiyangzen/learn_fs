<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/bin/cryfs.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/bin/cryfs.rs

Purpose: binary entry point for the `cryfs` executable.

Important APIs/types/functions: `main` returns `ExitCode` and delegates all parsing, setup, panic-hook behavior, and execution to `cryfs_cli_utils::run::<Cli>()`.

Control flow: the runner invokes the `Application` implementation in `Cli`, which handles immediate-exit paths, daemon mode, logging, Tokio runtime initialization, config loading, and mounting.

State and persistence: no direct state. All persistence is handled in library modules.

Dependencies/integration: imports `cryfs_cli::Cli`, making the binary a thin shell over the library crate.

Risks/test signals: the file is intentionally minimal. Integration tests in `cryfs-cli/tests/args.rs` execute the built binary, so this entry path is covered for argument behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/bin/cryfs.rs -->
