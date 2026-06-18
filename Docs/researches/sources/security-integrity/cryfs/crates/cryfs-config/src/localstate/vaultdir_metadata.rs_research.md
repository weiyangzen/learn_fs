<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/vaultdir_metadata.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/vaultdir_metadata.rs

Purpose: tracks which filesystem id was last seen at each vault directory path, detecting vault replacement at a stable location.

Important APIs/types/functions: `VaultdirMetadata` wraps a flattened `HashMap<PathBuf,VaultdirMetadataEntry>`. Methods `load`, `filesystem_id_for_vaultdir_is_correct`, `update_filesystem_id_for_vaultdir`, and `save` implement persistence. `CheckFilesystemIdError::FilesystemIdIncorrect` reports mismatches.

Control flow: CLI loads metadata, checks the current vault path against the config's filesystem id, optionally asks the user on mismatch, then updates/saves the mapping.

State and persistence: JSON stored at `LocalStateDir::for_vaultdir_metadata()` (`vaultdirs_v2.json`). Writes use `File::create` and pretty JSON.

Dependencies/integration: uses `FilesystemId` hex serde and `LocalStateDir`. The CLI currently performs the check; a TODO suggests config-file based checking in filesystem code may be better.

Risks/test signals: path keys are not canonicalized, so symlinks or relative paths can create separate entries. Writes are non-atomic. Tests are TODO.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/vaultdir_metadata.rs -->
