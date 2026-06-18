# sources/storage-engines/foundationdb/bindings/ruby/lib/fdbsubspace.rb

Purpose: This file implements Ruby subspaces: tuple-encoded key prefixes with helper methods for packing, unpacking, ranges, and nesting.

Important APIs and types: `FDB::Subspace` exposes `raw_prefix`, `[]`, `key`, `pack`, `unpack`, `range`, `contains?`, `as_foundationdb_key`, and `subspace`.

Control flow: Initialization concatenates a binary raw prefix with packed tuple prefix. Child subspaces append one tuple element. `pack` concatenates raw prefix with tuple packing; `unpack` validates prefix containment and decodes the suffix; `range` prepends prefix to tuple-layer range bounds.

State and persistence behavior: Only `@raw_prefix` is stored. Generated prefixes and keys define persistent application key layout.

Dependencies and integration points: It depends on `fdbtuple` and is used heavily by the Ruby directory layer and binding tester directory operations.

Risks: Prefix overlap and encoding mismatches can cause logical namespace collisions. Ruby string encoding must remain binary for raw key correctness.

Test signals: Directory tester operations cover subspace creation, nested opening, pack/unpack, range, containment, and use as FoundationDB keys.
