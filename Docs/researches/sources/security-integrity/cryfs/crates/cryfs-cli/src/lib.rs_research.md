<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/lib.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/lib.rs

Purpose: library root for the CLI crate.

Important APIs/types/functions: forbids unsafe code, declares modules `args`, `cli`, `console`, and `sanity_checks`, and re-exports `Cli`.

Control flow: no runtime flow here; `src/bin/cryfs.rs` uses the exported `Cli` as the application type.

State and persistence: none directly.

Dependencies/integration: invokes `cryfs_version::assert_cargo_version_equals_git_version!()` for package/version consistency. Internal modules perform actual config and mount behavior.

Risks/test signals: several crate-level TODOs call out missing mount lifecycle tests, unhelpful error messages, and foreground unmount UX. The root keeps those concerns visible but not enforced.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/lib.rs -->
