# sources/security-integrity/cryfs/crates/cryfs-version/build.rs

## Purpose
Build script that initializes `git2version` proxy build metadata for the version crate.

## Important APIs, types, and functions
- `main` calls `git2version::init_proxy_build!()`.

## Control flow
At build time, the macro emits or configures environment/proxy metadata used by `git2version::init_proxy_lib!()` in the library.

## State and persistence behavior
The script contributes compile-time build metadata rather than runtime state. It may cause Cargo rebuild behavior through generated environment/output controlled by `git2version`.

## Dependencies and integration points
Requires the build-dependency `git2version` with its `build` feature. Library macros rely on the metadata initialized here.

## Risks and edge cases
If git metadata is unavailable or the build script does not run as expected, downstream version info may lack git details or version assertions may behave differently.

## Test signals
Build success and version macro tests are the primary signal; there are no direct unit tests for the build script.
