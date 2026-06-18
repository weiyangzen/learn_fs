# sources/storage-engines/tikv/components/keys/src/rewrite.rs

## Purpose
`rewrite.rs` rewrites key prefixes and range bounds, mainly for features that remap data from one logical prefix to another while preserving range semantics.

## Important APIs, Types, and Functions
- `WrongPrefix` marks a source key or bound that cannot be rewritten.
- `encode_bound` applies TiKV byte encoding to included/excluded `Bound<Vec<u8>>` keys.
- `rewrite_prefix` replaces `old_prefix` with `new_prefix` when `src` starts with `old_prefix`.
- `rewrite_prefix_of_end_key` also handles the special case where the source end key is exactly the successor of `old_prefix`, mapping it to `next_key(new_prefix)`.
- `rewrite_prefix_of_start_bound` and `rewrite_prefix_of_end_bound` apply these rules to `Bound<&[u8]>`, converting empty-successor end keys to `Unbounded`.

## Control Flow
Start bounds are direct rewrites except that unbounded plus empty old prefix becomes an included new prefix. End bounds use exclusive-end-key semantics: excluded bounds may be successor-expanded, and an empty rewritten end key becomes unbounded.

## State and Persistence Behavior
No state is held. The output vectors may become persisted or used in scans, so correctness depends on retaining inclusive/exclusive boundary semantics after prefix replacement.

## Dependencies and Integration Points
The module uses `tikv_util::codec::bytes::encode_bytes` and `keys::next_key`. It is likely consumed by backup/import/restore or range rewrite paths that need byte-accurate key remapping.

## Risks
End-bound handling is subtle around all-`0xff` prefixes, empty prefixes, and inclusive vs exclusive bounds. Returning `Unbounded` from an empty next key is correct for "no upper bound" but dangerous if callers interpret empty as a normal key. `WrongPrefix` has no payload, so diagnostics must come from caller context.

## Test Signals
Tests cover direct rewrites, wrong prefixes, successor end-key rewrites, all-`0xff` boundary behavior, and full start/end range combinations for included, excluded, and unbounded bounds.
