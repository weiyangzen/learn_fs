# sources/security-integrity/cryfs/crates/cryfs-version/tests/cryfs-version.rs

## Purpose
Integration tests for the `cryfs-version` procedural/macros surface by creating temporary downstream Cargo projects that depend on the local crate.

## Important APIs, types, and functions
- Computes `OUR_CRATE_PATH` and `OUR_GITVERSION` from `cryfs_version::GITINFO`.
- Uses `TempProjectBuilder` to generate temporary Cargo.toml/main.rs pairs.
- Exercises `package_version!`, `cargo_version!`, and `assert_cargo_version_equals_git_version!`.
- Helpers run projects and assert either successful JSON version output or expected build stderr.

## Control flow
Each module builds a small crate with a chosen version, then runs `cargo run` through `tempproject`. Tests that require git tag metadata are skipped when `OUR_GITVERSION` is absent. Success paths parse stdout as JSON `Version`; mismatch paths assert build failure contains the constructor panic text.

## State and persistence behavior
State is isolated to temporary Cargo projects and their build outputs. The tests persist no repository state but depend on the current checkout's git metadata when available.

## Dependencies and integration points
Depends on Cargo, `tempproject`, Serde JSON, the local `cryfs-version` path dependency, and macro expansion/build-script behavior. It validates downstream-user integration rather than only in-crate units.

## Risks and edge cases
The mismatch tests are conditional, so non-git source archives do not exercise tag enforcement. Assertions depend on exact panic text in compiler/build stderr. Temporary projects pin edition 2024 and declare their own workspace to avoid inheriting the parent workspace.

## Test signals
Signals are successful downstream builds, parsed version equality, and failed builds containing the version-mismatch diagnostic.
