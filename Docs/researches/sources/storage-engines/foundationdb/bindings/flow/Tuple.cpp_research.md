## sources/storage-engines/foundationdb/bindings/flow/Tuple.cpp

Purpose: implements FoundationDB tuple wire encoding/decoding for Flow bindings, including type ordering, nested tuples, UUIDs, floats, doubles, booleans, ints, strings, nulls, and 96-bit versionstamps.

Important APIs and functions: constants define tuple type codes. Helpers handle string terminators, big-endian float/double conversion, and order-preserving floating point bit adjustment. `Tuple(StringRef)` parses packed data and computes element offsets. `append*` methods encode values. `get*` methods decode by type and index. `range`, `subTuple`, comparison operators, and `Uuid` methods complete the tuple API.

Control flow: unpack scans bytes, tracks nested tuple depth, and records offsets only at top level. String encodings escape embedded nulls as `\x00\xff`. Integers use variable-length signed encodings around `INT_ZERO_CODE`. Floats/doubles convert to sortable byte order. Nested tuple encoding escapes null elements and terminates with null.

State and persistence: owns packed tuple bytes in an arena-backed vector and an offsets vector. Packed bytes are persisted directly as keys or values by subspace and directory code.

Dependencies and integration points: depends on `fdb_flow.h`, `TupleVersionstamp`, endian helpers, Flow errors, and arena types. Used by C API mapped-range tests, directory layer metadata, subspaces, allocator candidates, and tester stack values.

Risks: decoding uses asserts for bounds in some paths and throws for invalid types/depth. Strict aliasing/alignment around float/int casts and endian conversion are portability-sensitive. Versionstamp size must remain 12 bytes for tuple-layer compatibility.

Test signals: latest C API unit tests cover versionstamp tuple behavior and mapped-range tuple mappers; directory tester exercises packing/unpacking across many operations.
