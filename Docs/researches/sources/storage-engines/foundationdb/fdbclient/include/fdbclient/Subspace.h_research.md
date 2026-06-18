<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Subspace.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Subspace.h

## Purpose
`Subspace.h` declares a small tuple-prefixed keyspace abstraction used by task buckets and other layers to pack, unpack, and range-query namespaced keys.

## Important APIs, Types, and Functions
`Subspace` exposes constructors from a `Tuple` and raw prefix, `key`, `contains`, `pack`, templated `pack`, string-specific `pack`, `unpack`, `range`, `subspace`, `get`, templated `get`, and string-specific `get`. It stores its raw prefix as `Standalone<VectorRef<uint8_t>>`.

## Control Flow
Callers construct a raw prefix, pack tuple elements by appending FoundationDB tuple encoding to the prefix, and derive child subspaces by extending the tuple path. `contains` checks whether a key has the subspace prefix; `unpack` removes the prefix and decodes the remaining tuple bytes; `range` returns the key range for the prefix plus optional tuple.

## State and Persistence Behavior
The object is an in-memory namespace descriptor. It does not persist data itself, but keys produced by it become durable database keys in users such as `TaskBucket`. The standalone prefix keeps packed memory alive across returned keys and child subspaces.

## Dependencies and Integration Points
It depends on Flow key types and `Tuple.h`. It integrates with `TaskBucket`, key-backed data structures, directory-like code, and any component that wants tuple-encoded sub-keyspaces.

## Risks and Edge Cases
`unpack` is only valid for keys contained by the prefix; callers should use `contains` or enforce namespacing. Raw prefixes can be arbitrary bytes, so collisions are possible if multiple owners choose overlapping prefixes. String packing requires the caller to choose byte-string versus UTF-8 tuple element semantics.

## Test Signals
Tuple pack/unpack tests, subspace range tests, task-bucket key layout tests, and boundary-key tests for prefix ranges are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Subspace.h -->
