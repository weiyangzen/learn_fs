# sources/security-integrity/cryfs/crates/cryfs-version/src/version.rs

## Purpose
Defines a generic semantic `Version<P>` type with parsing, const parsing, display/debug formatting, ordering, serde, and borrowed/owned prerelease conversions.

## Important APIs, types, and functions
- `Version<P>` stores `major`, `minor`, `patch`, and optional `prerelease`.
- `Display`/`Debug` emit `major.minor.patch[-prerelease]`.
- `PartialEq`, `Eq`, `Ord`, and `PartialOrd` compare major/minor/patch first, then prerelease, with prerelease less than stable.
- `Version<&str>::parse`, `parse_const`, `eq_const`, `to_owned`, and `into_owned`.
- `Version<String>::to_borrowed`.
- `ParseVersionError` wraps invalid numeric parse errors with the original string.

## Control flow
Parsing splits once on `-`, then up to two `.` separators, defaulting missing minor or patch to zero. Runtime parsing uses standard `str::parse`; const parsing uses `konst::string` and `u32::from_str_radix`. Comparison exits early on numeric differences and then compares prerelease strings lexicographically or stable/prerelease presence.

## State and persistence behavior
The type is value-only and serde-serializable. It persists as JSON fields when serialized and as display strings when formatted.

## Dependencies and integration points
Used by `VersionInfo`, crate macros, and downstream build identifiers. Depends on serde, `derive_more` for error display, `konst` for const parsing, and standard borrow/comparison traits.

## Risks and edge cases
Parsing is permissive for shortened versions and does not validate full SemVer prerelease grammar beyond numeric components. `split_once('-')` treats everything after the first dash as prerelease. Lexicographic prerelease ordering is simpler than full SemVer identifier ordering. `parse_const` returns only `ParseIntError`, losing original string context.

## Test signals
In-file tests cover runtime and const parsing, display/debug, equality/order across borrowed and owned forms, shortened-version equivalence, prerelease ordering, serde JSON round trips/format, and ownership conversions.
