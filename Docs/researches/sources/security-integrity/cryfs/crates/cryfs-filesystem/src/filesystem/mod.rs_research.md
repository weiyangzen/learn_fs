# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/mod.rs

## Purpose
Declares the filesystem module layout and exposes the public filesystem entry type.

## Important APIs, types, and functions
- Private modules: `device`, `dir`, `file`, `node`, `node_info`, `open_file`, and `symlink`.
- Public export: `pub use device::CryDevice`.

## Control flow
There is no runtime control flow. The file is a module boundary that hides implementation adapters while keeping `CryDevice` available to external crates.

## State and persistence behavior
No state is stored here. Persistence is handled by the submodules, especially `device.rs`, `dir.rs`, `node_info.rs`, and `open_file.rs`.

## Dependencies and integration points
This module is consumed by `cryfs-filesystem/src/lib.rs` and by `cryfs-runner`, which imports `cryfs_filesystem::filesystem::CryDevice`.

## Risks and edge cases
Because only `CryDevice` is exported, downstream code cannot directly name internal adapter types except through associated types. That is a deliberate encapsulation boundary but can complicate integration tests that want to inspect internals.

## Test signals
Compile-time tests and downstream crate builds are the primary signal: if module visibility or exports regress, `cryfs-runner` and RustFS integrations fail to compile.
