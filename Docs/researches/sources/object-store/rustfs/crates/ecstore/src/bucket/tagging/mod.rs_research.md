# sources/object-store/rustfs/crates/ecstore/src/bucket/tagging/mod.rs

## Purpose
This module provides helpers to parse and format S3 tag query strings using URL form encoding.

## Important APIs, Types, and Functions
- `decode_tags(tags: &str) -> Vec<Tag>` parses `k=v&...`, skips empty keys, creates `s3s::dto::Tag` values, and sorts by key.
- `decode_tags_to_map(tags: &str) -> HashMap<String, String>` parses into a map, also skipping empty keys. Duplicate keys keep the last parsed value.
- `encode_tags(tags: Vec<Tag>) -> String` form-encodes tags with both key and value present, skipping incomplete DTOs.

## Control Flow and State Behavior
All functions are pure conversions. Parsing delegates to `url::form_urlencoded::parse`; encoding delegates to `form_urlencoded::Serializer`. Sorting in `decode_tags` gives deterministic vector order.

## Dependencies and Integration Points
It depends on `s3s::dto::Tag`, `url::form_urlencoded`, and `HashMap`. This module is likely used by bucket/object tagging APIs and replication/lifecycle code that needs deterministic tag matching.

## Persistence
No persistence. It converts between wire query-string form and DTO/map shapes.

## Risks and Edge Cases
`decode_tags_to_map` loses duplicate tag keys silently. `encode_tags` preserves caller-provided order rather than sorting, so round-trip string equality is not guaranteed. Empty values are preserved; empty keys are dropped. No S3 tag limits, character constraints, or maximum encoded length validation are enforced here.

## Test Signals
No inline tests. Good coverage would include URL escaping, duplicate keys, empty key/value handling, sort ordering, and encode/decode round trips.
