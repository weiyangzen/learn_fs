## sources/storage-engines/foundationdb/bindings/flow/Subspace.h

Purpose: declares the Flow subspace abstraction for prefixing tuple-encoded keys.

Important APIs and types: constructors accept a `Tuple` plus raw prefix or raw prefix alone. Methods expose `key`, `contains`, `pack`, `unpack`, `range`, `subspace`, and `get`, with template and string convenience overloads. `packNested` and `getNested` handle nested tuple items.

Control flow: callers build typed tuple keys without manually concatenating byte prefixes. Child subspaces are derived by appending packed tuple elements to the current raw prefix.

State and persistence: stores `Standalone<VectorRef<uint8_t>> rawPrefix`, preserving prefix bytes across async use.

Dependencies and integration points: includes Flow, `fdb_flow.h`, and `Tuple.h`; inherited by `DirectorySubspace`.

Risks: template overloads rely on `Tuple::append` support for each type. Invalid unpacking throws at runtime rather than returning optional.

Test signals: used heavily by tuple, directory, and allocator code paths.
