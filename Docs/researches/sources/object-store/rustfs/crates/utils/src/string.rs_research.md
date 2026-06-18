# sources/object-store/rustfs/crates/utils/src/string.rs

## Purpose
Implements string parsing and pattern helpers for booleans, wildcard matching, suffix checks, case-insensitive prefixes, and MinIO-style ellipsis expansion.

## Important APIs, Types, And Functions
`parse_bool` and `parse_bool_with_default` accept selected true/false spellings. `match_simple`, `match_pattern`, `has_pattern`, `match_as_pattern_prefix`, and private `deep_match_rune` implement `*`/`?` wildcard matching. `has_string_suffix_in_slice` performs case-insensitive suffix matching with `*` wildcard. `Pattern` stores an ellipsis prefix/suffix and sequence; `ArgPattern` stores multiple patterns and expands cartesian products. `has_ellipses`, `find_ellipses_patterns`, and `parse_ellipses_range` detect and expand `{N...M}` decimal/hex ranges up to 10,000 entries.

## Control Flow And State
Only `ELLIPSES_RE` is global lazy state. Wildcard matching is recursive and byte-based. Ellipsis parsing uses regex captures from the rightmost matching group, builds patterns, rejects leftover braces, detects hex by A-F characters, preserves padding based on the end bound width, and rejects descending/oversized ranges.

## Dependencies And Integration Points
Uses `regex` and `std::io::Error`. Exposed under the `string` feature and likely feeds command-line/config expansion and matching logic elsewhere in RustFS.

## Risks And Test Signals
Wildcard matching operates on bytes, not Unicode scalar values; `?` can split UTF-8. Recursive `*` matching can be expensive on adversarial patterns. Boolean parsing is not fully case-insensitive for words like `Enabled`. Ellipsis expansion can still generate large cartesian products across multiple ranges because the per-range cap is 10,000. Tests heavily cover ellipsis detection/parsing, hex/padded ranges, invalid formats, oversize rejection, and Windows GUID false positives.
