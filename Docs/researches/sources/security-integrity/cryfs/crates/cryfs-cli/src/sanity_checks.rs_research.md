<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/sanity_checks.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/sanity_checks.rs

Purpose: pre-mount filesystem sanity checks for vault and mount directories.

Important APIs/types/functions: `check_dir_accessible` verifies existence, optionally prompts/creates, ensures the path is a directory, and calls `check_dir_writeable_and_readable`. That helper writes and reads a `.cryfs_testfile` through `TempFile`, then scans directory entries via `dir_contains_file`. `check_mountdir_doesnt_contain_vaultdir` rejects vault directories inside the mountpoint.

Control flow: async Tokio filesystem calls avoid blocking. Missing paths use command-line create flags or callback prompts. Errors are contextualized with `anyhow`.

State and persistence: may create directories and a temporary test file, which `TempFile` cleans up. Does not persist CryFS metadata.

Dependencies/integration: called by `Cli::sanity_checks` before config load/mount. Uses `cryfs_utils::tmpfile::TempFile`.

Risks/test signals: TODOs note errors should map to dedicated CLI error codes, and there are no local tests. The mountdir/vaultdir containment check is path-prefix based and may need canonicalization scrutiny.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/sanity_checks.rs -->
