## sources/security-integrity/cryfs/crates/cli-utils/src/lib.rs

Purpose: crate root for shared CryFS CLI utilities, defining public module surface and safety policy.

Important APIs and exports: forbids unsafe code. Re-exports `parse_path`, password provider module, environment docs/types, `Application`, `DEFAULT_LOG_LEVEL`, `run`, `print_config`, `CliError` helpers, blockstore setup APIs, and `clap_logflag`. It also exposes `reexports_for_tests` for downstream integration tests needing exact dependency instances.

Control flow and state: no runtime control flow beyond the compile-time `cryfs_version::assert_cargo_version_equals_git_version!()` macro, which ensures package version and git-derived version stay aligned.

Dependencies and integration: module declarations wire `path`, `args`, `password_provider`, `version`, `env`, `application`, `config`, `error`, and `blockstore_setup`. The crate is consumed by multiple binaries and by the check-test fixture.

Risks and test signals: the public re-export surface is a compatibility boundary. `#![forbid(unsafe_code)]` is a meaningful safety signal for CLI glue around cryptographic filesystem operations.
