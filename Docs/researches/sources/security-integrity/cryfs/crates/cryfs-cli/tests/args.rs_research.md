<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/tests/args.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/tests/args.rs

Purpose: binary-level argument tests for the real `cryfs` executable.

Important APIs/types/functions: lazy statics build current, debug, and release binary paths using `assert_cmd::cargo_bin!` and `escargot::CargoBuild`. Helpers `cryfs_cmd`, `cryfs_cmd_debug`, and `cryfs_cmd_release` construct commands.

Control flow: test modules cover no-args failure, help, version exclusivity, `--show-ciphers`, incomplete foreground invocations, debug-build warning behavior, and hidden/exclusive/manual rejection behavior for `--daemon`.

State and persistence: debug/release builds create Cargo build artifacts. Tests do not create vaults or mount filesystems.

Dependencies/integration: validates the compiled binary, `cryfs_config::CRYFS_VERSION`, `ALL_CIPHERS`, clap output, and `cryfs_runner::run_as_background_daemon` fd checks for manual daemon invocation.

Risks/test signals: strong coverage for immediate CLI parse behavior, but many TODOs remain for successful mounting, update checks, path handling, env-var help, git warnings, and invalid argument usage details. Tests depend on exact clap/error strings.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/tests/args.rs -->
