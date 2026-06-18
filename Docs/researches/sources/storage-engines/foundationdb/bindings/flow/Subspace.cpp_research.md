## sources/storage-engines/foundationdb/bindings/flow/Subspace.cpp

Purpose: implements tuple-based subspace key packing, unpacking, range construction, containment, and nested subspace derivation.

Important APIs and functions: constructors combine raw prefixes and packed tuples into `rawPrefix`. `key` returns the prefix. `pack` prefixes packed tuple bytes. `unpack` validates containment before tuple unpacking. `range` builds `[prefix+tuple+\x00, prefix+tuple+\xff)` key ranges. `contains`, `subspace`, and `get` provide prefix checks and child subspaces.

Control flow: range/key construction uses arena-backed vectors inside returned `Standalone`/`KeyRange` values. `unpack` throws `key_not_in_subspace` on invalid prefixes.

State and persistence: owns only an in-memory `rawPrefix`; no database IO. Persistent behavior is by convention: all keys packed through the subspace share the prefix.

Dependencies and integration points: uses `Tuple`, `FDBLoanerTypes`, and Flow arenas. Directory handles inherit this behavior through `DirectorySubspace`.

Risks: range boundaries rely on the tuple layer guarantee that appending `\x00` and `\xff` captures all child tuple encodings. Comments note a desired test around arena usage.

Test signals: directory tester pack/unpack/range/contains/open_subspace instructions validate these methods.
