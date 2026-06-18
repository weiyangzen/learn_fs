# sources/object-store/rustfs/crates/policy/src/policy/utils/wildcard.rs

## Purpose

Provides wildcard matching primitives for actions, resources, principals, and pattern-prefix checks. It supports `*` for arbitrary byte sequences and `?` for single-byte matching, with a special simple mode used by principal matching.

## Important APIs, Types, and Functions

- `is_simple_match(pattern, name)` calls `inner_match(..., simple = true)`.
- `is_match(pattern, name)` calls `inner_match(..., simple = false)`.
- `is_match_as_pattern_prefix(pattern, text)` tests whether text is compatible with the beginning of a wildcard pattern, stopping true at `*`.
- `inner_match` handles empty pattern and global `*` fast paths.
- `deep_match` recursively matches bytes for `?`, `*`, and literals.

## Control Flow

Strict matching requires `?` to consume an existing byte and final pattern exhaustion to coincide with name exhaustion. Simple matching differs when `?` sees an empty name: it returns true, allowing a trailing question mark to match an absent byte. `*` branches recursively over zero-character and one-or-more-character consumption. Prefix matching walks pattern/text pairs and accepts as soon as it reaches a `*`; `?` skips one text byte.

## State and Persistence

Pure stateless functions; no persistence.

## Dependencies and Integration Points

Used by `Resource` matching, string condition `StringLike`, action matching elsewhere in the policy module, and principal matching. Differences between strict and simple modes are important for principal behavior versus resource/action behavior.

## Risks and Edge Cases

- `deep_match` is recursive and can be exponential for adversarial patterns with many `*` branches and long names.
- Matching is byte-oriented, not Unicode scalar-aware. `?` matches one byte, not one Unicode character.
- `is_simple_match` permits `a?` to match `a`, unlike strict matching; use the correct API for the domain.

## Test Signals

Inline tests cover action-like patterns, bucket/object resource patterns, strict `?` behavior, simple-mode trailing `?` behavior, long wildcard path cases, and prefix-match semantics.
