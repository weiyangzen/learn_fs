# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/lib.rs

## Purpose
Defines the public root of the `cryfs-filesystem` crate and exposes the filesystem module.

## Important APIs, types, and functions
- Applies `#![forbid(unsafe_code)]`.
- Allows private rustdoc intra-doc links temporarily.
- Public module: `pub mod filesystem`.
- Calls `cryfs_version::assert_cargo_version_equals_git_version!()`.

## Control flow
There is no runtime control flow. The version macro expands at compile time and checks Cargo/git version consistency.

## State and persistence behavior
No runtime or persistent state is stored here.

## Dependencies and integration points
Integrates the crate with `cryfs-version` compile-time version policy and exposes `filesystem::CryDevice` through the nested module.

## Risks and edge cases
The TODO indicates the public API is not settled. Tight compile-time version checking can break builds if Cargo package version and git tags diverge.

## Test signals
The main signal is successful compilation under `forbid(unsafe_code)` and successful expansion of the version assertion macro.
