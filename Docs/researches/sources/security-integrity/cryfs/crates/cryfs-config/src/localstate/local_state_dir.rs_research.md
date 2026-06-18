<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/local_state_dir.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/local_state_dir.rs

Purpose: path helper for local CryFS state files.

Important APIs/types/functions: `LocalStateDir { app_dir }`, `new`, `for_filesystem_id`, and `for_vaultdir_metadata`.

Control flow: `for_filesystem_id` creates `<app_dir>/filesystems/<filesystem_id_hex>` and returns it. `for_vaultdir_metadata` creates `<app_dir>` and returns `<app_dir>/vaultdirs_v2.json`.

State and persistence: creates directories as needed. Does not read or write metadata content itself.

Dependencies/integration: used by filesystem metadata and vaultdir metadata modules, and constructed by CLI from the environment local-state directory.

Risks/test signals: directory creation is eager and uses default permissions. TODO notes tests are missing. Path construction relies on stable filesystem-id hex encoding.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/local_state_dir.rs -->
