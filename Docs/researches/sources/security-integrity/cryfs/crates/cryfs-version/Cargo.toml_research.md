# sources/security-integrity/cryfs/crates/cryfs-version/Cargo.toml

## Purpose
Cargo manifest for the `cryfs-version` crate, which provides semantic version types, git metadata integration, and compile-time version consistency macros.

## Important APIs, types, and functions
- Package metadata inherits workspace settings and version.
- Dependencies: `git2version`, `konst`, serde derive, and `derive_more`.
- Build dependency enables `git2version` build support.
- Dev dependencies include `predicates`, `serde_json`, and local `tempproject`.

## Control flow
The manifest enables build-script generated git metadata and compile-time const parsing/comparison support through `konst`.

## State and persistence behavior
No direct runtime state. Build output from `git2version` becomes compile-time metadata for the crate.

## Dependencies and integration points
Consumed by other CryFS crates through version macros. Dev dependencies support macro/build integration and serialization tests.

## Risks and edge cases
The crate's own version comes from workspace version; mismatches with git tags can fail dependent crate builds through assertions. `git2version` behavior determines availability and exact shape of git metadata.

## Test signals
`cargo test -p cryfs-version` should validate parsing, serde, display, ownership conversions, and version macro behavior.
