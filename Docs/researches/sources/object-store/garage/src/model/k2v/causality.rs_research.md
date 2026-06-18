# sources/object-store/garage/src/model/k2v/causality.rs

## Purpose
This file implements K2V causality tokens using vector clocks. The token records which per-node versions have been seen by a client so later writes/deletes can discard causally older values while preserving concurrent conflicts.

## Important APIs, types, and functions
`K2VNodeId` is a `u64` abbreviation of a Garage UUID. `VectorClock` is `BTreeMap<K2VNodeId, u64>`. `make_node_id` uses the first eight bytes of a node UUID. `vclock_gt` checks if one clock has any component greater than another; `vclock_max` merges clocks by max. `CausalContext` wraps a vector clock and exposes `new`, `serialize`, `parse`, and `is_newer_than`.

## Control flow
Serialization flattens sorted `(node,time)` pairs into u64s, prepends an XOR checksum, and encodes bytes using URL-safe base64 without padding. Parsing validates byte length, reconstructs the map, recomputes the checksum, and returns `None` on malformed tokens.

## State and persistence behavior
The structure is stored in K2V items and exposed as an API token string. It is deterministic because `BTreeMap` orders entries. The checksum is only corruption detection, not authentication.

## Dependencies and integration points
It depends on `base64`, `serde`, and `garage_util::data::Uuid`. `K2VItem::update`, polling APIs, range seen markers, and K2V clients use these tokens to express causal context.

## Risks and edge cases
`make_node_id` truncates 256-bit node IDs to 64 bits, so collisions are possible in theory. `vclock_gt` means "has some newer component," not a full partial-order domination check. The XOR checksum is weak against intentional tampering, so API authorization must not rely on it. Very large clocks inflate headers/tokens.

## Test signals
`test_causality_token_serialization` verifies round-trip for a nontrivial vector clock. Additional tests should cover invalid base64, bad lengths, checksum mismatch, empty clocks, and collision behavior assumptions.
