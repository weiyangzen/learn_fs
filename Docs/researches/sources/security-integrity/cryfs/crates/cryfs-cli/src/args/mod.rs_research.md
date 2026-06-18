<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/mod.rs -->
# sources/security-integrity/cryfs/crates/cryfs-cli/src/args/mod.rs

Purpose: argument module facade for the CLI crate.

Important APIs/types/functions: declares `cryfs_args`, `fuse_option`, and `mount_args`, then re-exports `CryfsArgs`, `AtimeOption`, `FuseOption`, and `MountArgs`.

Control flow: no runtime control flow. It provides a stable import surface to `cli.rs`.

State and persistence: none.

Dependencies/integration: keeps parser modules private except for the types consumed by the main CLI orchestration.

Risks/test signals: small facade; any parser type rename or visibility change will break imports at compile time. No separate tests needed beyond parser integration tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-cli/src/args/mod.rs -->
