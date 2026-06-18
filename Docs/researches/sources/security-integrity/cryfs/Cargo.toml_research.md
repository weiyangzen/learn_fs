<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/Cargo.toml -->
# sources/security-integrity/cryfs/Cargo.toml

**Purpose**
This root manifest defines the CryFS Rust workspace, shared package metadata, and centralized dependency versions.

**Important APIs, Types, And Functions**
It declares `members = ["crates/*"]`, resolver 3, workspace package metadata such as edition 2024, rust-version 1.95, LGPL license, repository/homepage, and version `2.0.0-alpha3`. `[workspace.dependencies]` centralizes crypto, async, CLI, FUSE, testing, serialization, logging, compression, and utility crates.

**Control Flow**
Cargo uses this manifest to resolve all workspace crates and dependency versions. Member crates can inherit package metadata and dependency versions from the workspace.

**State And Persistence**
The file controls build dependency resolution and package metadata. It does not define runtime state.

**Dependencies And Integration Points**
Every `crates/*` member integrates through this workspace. CI uses the workspace root for broad `cargo test`, `cargo doc`, and coverage runs.

**Risks**
Centralized versions reduce drift but make upgrades affect many crates at once. Several TODOs indicate metadata and dependency feature trimming are not complete. The MSRV is high and enforced in CI.

**Test Signals**
The CI matrix validates that the workspace resolves and builds/tests under stable, nightly, and Rust 1.95.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/Cargo.toml -->
