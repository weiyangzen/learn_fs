# sources/security-integrity/cryfs/crates/check/src/console.rs

Purpose: `RecoverConsole` implements the `cryfs_config::config::Console` trait for config loading during check operations.

Important APIs and flow: Every prompt-like method currently calls `todo!()`: migration, changed encryption key, replaced filesystem, single-client-mode decisions, new filesystem settings, cipher/blocksize prompts, and creating directories.

State and persistence: The console stores no state. Its methods would normally gate config or local-state decisions, but this check path expects read-only existing filesystems and should not create or migrate vaults.

Dependencies and integration: It is passed to `cryfs_config::config::load_readonly` in `cli.rs`. It depends on `ScryptSettings`, `Byte`, `Version`, `VersionInfo`, and path types required by the trait.

Risks and test signals: Any config load path that asks a question will panic. This is a major operational limitation for vaults requiring migration, changed-key confirmation, replaced-filesystem confirmation, or missing directory creation prompts.
