## sources/security-integrity/cryfs/crates/cli-utils/Cargo.toml

Purpose: package manifest for shared command-line utility code used by CryFS executables such as `cryfs` and `cryfs-check`.

Important declarations: package metadata is inherited from the workspace. Dependencies include `clap` with derive support, `clap-logflag`, `human-panic`, `rpassword`, `path-absolutize`, `dirs`, and internal crates `cryfs-config`, `cryfs-blockstore`, `cryfs-version`, `cryfs-utils`, and `cryfs-crypto`. `reqwest` and `serde_json` are optional. The default feature enables `check_for_updates`, which activates those optional network/JSON dependencies.

Control flow and state: no runtime logic exists in the manifest, but feature selection changes whether version display performs HTTP update checks and whether environment variables such as `CRYFS_NO_UPDATE_CHECK` are compiled in.

Dependencies and integration: dev dependencies include CLI assertion, environment mutation, temp project, and test utility crates. This manifest is the dependency boundary for the fixture in `check/tests/common/fixture.rs`, which uses `setup_blockstore_stack_dyn`.

Risks and test signals: default network-update behavior adds privacy and reliability considerations for CLI startup, mitigated by environment/noninteractive checks in code. Version synchronization is guarded in `lib.rs` by a cargo/git version assertion.
