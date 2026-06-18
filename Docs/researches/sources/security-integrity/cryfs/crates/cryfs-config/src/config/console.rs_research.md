<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/console.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/console.rs

Purpose: trait defining all user interactions required by config creation/loading.

Important APIs/types/functions: `Console` asks about filesystem migration, changed encryption key, replaced filesystem id, disabling single-client mode, new-filesystem single-client mode, scrypt settings, cipher, blocksize, and missing vault/mount directory creation.

Control flow: config loader/creator invoke these methods when command-line flags do not preselect behavior or when local-state mismatch needs user acceptance.

State and persistence: trait itself has no state. Implementations influence whether config/local-state is created, migrated, rewritten, or rejected.

Dependencies/integration: returns `anyhow::Result`, `ScryptSettings`, `Byte`, and version metadata. Implemented by `cryfs-cli::InteractiveConsole`.

Risks/test signals: the trait mixes config-specific and CLI-directory prompts; TODOs suggest splitting. Noninteractive implementations must be careful to avoid blocking prompts.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/console.rs -->
