# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/subspace_impl.py

## Purpose
This module implements the Python tuple subspace abstraction: a stable byte prefix plus helpers for packing/unpacking tuple keys and ranges under that prefix.

## Important APIs, Types, And Functions
`Subspace.__init__(prefixTuple=(), rawPrefix=b"")` computes `rawPrefix` with `fdb.tuple.pack`. `__getitem__` and `subspace()` derive child subspaces. `key`, `pack`, `pack_with_versionstamp`, `unpack`, `range`, `contains`, and `as_foundationdb_key` provide the key-building API used by directory and metadata code.

## Control Flow
The class is simple and immutable in practice. Construction packs a tuple under a raw prefix. Packing appends a tuple encoding to `rawPrefix`; unpacking first checks that the key starts with the prefix, then calls `fdb.tuple.unpack` with a prefix offset. Range construction delegates to `fdb.tuple.range` and then prepends `rawPrefix` to the resulting start/stop.

## State And Persistence Behavior
`Subspace` holds only an in-memory byte prefix. It does not read or write FDB, but its output controls which persistent keys callers read, write, or clear. Incorrect prefixes can redirect destructive operations to the wrong key range.

## Dependencies And Integration Points
It depends entirely on `fdb.tuple`. `DirectoryLayer`, application code, and transaction helpers can pass `Subspace` instances wherever `as_foundationdb_key` is accepted by `impl.keyToBytes`.

## Risks And Edge Cases
`unpack` raises when the key is outside the subspace. `range()` returns all tuple extensions of a tuple, not arbitrary prefix bytes, which matters for callers expecting raw byte prefix behavior. Versionstamp packing requires exactly one incomplete versionstamp through the tuple layer.

## Test Signals
Tests should cover nested subspaces, byte prefix containment, round-trip pack/unpack, range start/stop correctness, rejection of keys outside the subspace, and versionstamp packing behavior.
