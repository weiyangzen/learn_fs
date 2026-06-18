# sources/security-integrity/cryfs/crates/cryfs-version/src/lib.rs

## Purpose
Public API root for CryFS version management: exports `Version`, `VersionInfo`, git metadata setup, and macros for package version and Cargo/git consistency.

## Important APIs, types, and functions
- Crate attributes forbid unsafe code and deny missing docs.
- `git2version::init_proxy_lib!()` imports generated git metadata.
- Exports `Version` and `VersionInfo`.
- `package_version!` returns const `VersionInfo` after asserting Cargo/git consistency.
- `cargo_version!` builds a const `Version<&'static str>` from `CARGO_PKG_VERSION_*`.
- `assert_cargo_version_equals_git_version!` creates a module-level const assertion.

## Control flow
Macros expand in the caller's crate context for Cargo package version, while `GITINFO` comes from the version crate's generated metadata. `package_version!` first invokes the assertion macro, then constructs `VersionInfo::new(cargo_version!(), GITINFO)`.

## State and persistence behavior
All state is compile-time constants and generated git metadata. No runtime persistence.

## Dependencies and integration points
Used by `cryfs-filesystem` and `cryfs-runner` to enforce version consistency and expose build identity. Depends on `version.rs`, `version_info.rs`, and `git2version`.

## Risks and edge cases
Macros use `env!`, so malformed Cargo version env vars cause compile-time panic. Git tag parsing and consistency are const-time; mismatches break builds. The docs state package version includes git metadata, but this depends on `GITINFO` availability.

## Test signals
Downstream crates compiling with `assert_cargo_version_equals_git_version!` and any macro-specific tests in the crate validate expansion and consistency behavior.
