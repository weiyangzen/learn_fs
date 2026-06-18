<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/Cargo.toml -->
# sources/security-integrity/cryfs/crates/cryfs-cli/Cargo.toml

Purpose: manifest for the `cryfs-cli` package and `cryfs` binary.

Important APIs/types/functions: declares `[[bin]] name = "cryfs"` and package metadata from the workspace. The binary entry is `src/bin/cryfs.rs`, backed by library type `Cli`.

Control flow: feature set includes default empty features and optional `tokio_console`. Tests build both debug and release binaries through `escargot`.

State and persistence: no runtime state; dependency and feature configuration determines CLI, config, runner, and local-state capabilities.

Dependencies/integration: links `cryfs-cli-utils`, `cryfs-config`, `cryfs-runner`, `cryfs-blockstore`, `cryfs-utils`, `cryfs-version`, clap/logging/dialoguer/progress dependencies, and test dependencies such as `assert_cmd`, `escargot`, `lazy_static`, and `predicates`.

Risks/test signals: manifest dependency graph is broad because the CLI orchestrates config, runner, and local state. Cargo-level tests verify command-line behavior, but actual mount flows remain TODO-covered rather than fully tested here.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/Cargo.toml -->
