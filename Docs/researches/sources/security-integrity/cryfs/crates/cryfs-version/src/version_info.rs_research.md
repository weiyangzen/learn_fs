# sources/security-integrity/cryfs/crates/cryfs-version/src/version_info.rs

## Purpose
Defines `VersionInfo`, the crate's combined semantic-version and git-metadata value. It is the display/serialization boundary used by `cryfs-version` macros to report package versions and to enforce Cargo.toml-versus-git-tag consistency.

## Important APIs, types, and functions
- `VersionInfo<'b, 'c, P>` stores a `Version<P>` plus optional `git2version::GitInfo`.
- `VersionInfo::new` is a `const fn` for `&str` prereleases that parses `gitinfo.tag_info.tag` and panics if it differs from the Cargo version.
- `assert_cargo_version_equals_git_version` returns `self` after constructor validation, supporting macro-generated const chains.
- `version`, `gitinfo`, `Display`, and `Debug` expose read-only state and render release/git suffixes.

## Control flow
Construction optionally inspects git tag metadata, parses the tag into `Version`, compares with `eq_const`, and panics on mismatch. Formatting always writes the semantic version first, then appends `+<commits>.g<commit>` for builds after a tag, `.modified` for dirty after-tag builds, or `+modified` for dirty on-tag builds.

## State and persistence behavior
The struct is immutable after construction and derives `Serialize`/`Deserialize`, so its persisted shape includes both nested `version` and nullable `gitinfo`. It does not fetch git state itself; it trusts `git2version` output passed by generated build-time code.

## Dependencies and integration points
Integrates with `Version`, `git2version::GitInfo`, `konst` const parsing/unwrap, Serde lifetime bounds, and the public version macros in the surrounding crate. Display output is likely user-facing CLI/log text.

## Risks and edge cases
Const panic message is intentionally generic until const formatting is stable. A git tag that is present but not parseable as this crate's `Version` format panics through `konst::result::unwrap!`. Display hides commit id when exactly on a clean tag, so diagnostics rely on `gitinfo()` for full metadata.

## Test signals
Unit tests cover Display/Debug combinations for prerelease, commits-since-tag, dirty tree, on-tag builds, accessors, and Serde round trips into owned `String` prerelease storage.
