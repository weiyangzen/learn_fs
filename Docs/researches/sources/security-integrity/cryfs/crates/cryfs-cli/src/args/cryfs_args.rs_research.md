<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/cryfs_args.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/args/cryfs_args.rs

Purpose: top-level clap parser for the `cryfs` command.

Important APIs/types/functions: `CryfsArgs` flattens optional `MountArgs`, has `--show-ciphers` in an immediate-exit group conflicting with mounting, and hidden exclusive `--daemon`. `footer` renders environment-variable help from `cryfs_cli_utils::ENV_VARS_DOCUMENTATION`.

Control flow: clap decides whether mount args are present or an immediate-exit path is selected. `--daemon` is hidden and exclusive so normal users cannot combine it with other flags; actual daemon validity is checked later by runner bootstrap.

State and persistence: parser state only. No files are touched.

Dependencies/integration: depends on clap derive, color-print formatting, `MountArgs`, and shared CLI-utils env-var docs. `Cli::main` consumes these parsed fields.

Risks/test signals: tests in `cryfs-cli/tests/args.rs` cover help/version/show-ciphers and daemon flag hiding/exclusivity. Help footer output has TODO coverage gaps.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/cryfs_args.rs -->
