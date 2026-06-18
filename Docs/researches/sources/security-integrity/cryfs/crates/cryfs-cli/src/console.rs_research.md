<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/console.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/console.rs

Purpose: interactive terminal implementation of the `cryfs_config::config::Console` trait.

Important APIs/types/functions: `InteractiveConsole` stores an `OnceCell<bool>` for the "use default creation settings" answer. It implements migration, replaced-filesystem, changed-key, single-client-mode, scrypt-settings, cipher, blocksize, vaultdir, and mountdir prompts. Helpers `ask_yes_no`, `ask_multiple_choice`, `format_explanation`, `kb`, and `mb` centralize dialoguer UI.

Control flow: creation settings first ask whether defaults should be used; if yes, later creation prompts return defaults without asking. Otherwise, `dialoguer::Confirm` and `Select` drive terminal interaction.

State and persistence: only transient prompt state in `OnceCell`. Choices affect config creation and local-state acceptance in other modules.

Dependencies/integration: uses `dialoguer`, `byte_unit`, `cryfs_crypto::kdf::scrypt::ScryptSettings`, `cryfs_config::Console`, and version types.

Risks/test signals: TODOs note console appearance and flows need tests. Noninteractive mode still returns `InteractiveConsole`, so caller paths must avoid prompts via flags or dedicated password providers where needed.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/console.rs -->
