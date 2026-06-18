# sources/object-store/garage/src/model/k2v/seen.rs

## Purpose
This file implements `RangeSeenMarker`, the K2V poll-range continuation token. It compactly records globally seen per-node timestamps plus item-specific vector clocks so subsequent polls can return only new/unseen items.

## Important APIs, types, and functions
`RangeSeenMarker` stores a global `vector_clock` and per-sort-key item clocks. `new`, `restrict`, `mark_seen_node_items`, `canonicalize`, `encode`, `decode`, `decode_helper`, and `is_new_item` are the main methods.

## Control flow
Before a range poll, `restrict` narrows item-specific markers to the requested start/end/prefix. When node responses arrive, `mark_seen_node_items` raises the global clock for values produced by that node and records item-specific clocks for items still newer than the global clock. `canonicalize` drops per-item entries covered by the global clock. Encoding serializes with Garage's nonversioned msgpack helper, compresses with zstd, and base64-encodes. Decoding reverses that and returns `None` on malformed input.

## State and persistence behavior
Seen markers are client-visible continuation strings, not server-side state. They can grow with sparse per-item clocks but canonicalization keeps them smaller when full node ranges have been observed.

## Dependencies and integration points
It depends on K2V causality, item table, poll ranges, zstd, base64, Garage encode helpers, and helper bad-request conversion. `K2VRpcHandler::poll_range` uses it to filter responses and return new markers.

## Risks and edge cases
The marker is not authenticated; malicious clients can ask to skip data by supplying a broad marker. This is acceptable only if markers are treated as client-controlled cursors. Prefix restriction removes item-specific markers outside the prefix but keeps the global vector clock, which can still suppress old items from the same nodes. Large conflict sets can produce large tokens despite compression.

## Test signals
No local tests. Useful tests should cover encode/decode, range restriction for start/end/prefix, canonicalization, malicious/invalid strings, and `is_new_item` against global and per-item clocks.
