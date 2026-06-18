<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Tuple.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Tuple.h

## Purpose
`Tuple.h` declares FoundationDB tuple packing and unpacking support for C++ code, including primitive types, byte and UTF-8 strings, nested tuples, versionstamps, and user-defined tuple element codes.

## Important APIs, Types, and Functions
Important members include `Tuple::UnicodeStr`, `Tuple::UserTypeStr`, static `unpack`, `tupleToString`, `unpackUserType`, append overloads for strings, integers, bool, float, double, null, `TupleVersionstamp`, and user types, `pack`, `makeTuple`, `getType`, typed getters, `subTupleRawString`, `range`, `subTuple`, `getData`, and `getDataAsStandalone`.

## Control Flow
Callers build tuples by appending values, producing a packed byte string that preserves FoundationDB tuple ordering. Unpack parses a packed string into offsets and optional incomplete numeric filtering. Getters inspect the element type at a stored offset and decode the requested value. `range` computes the key range represented by a tuple prefix.

## State and Persistence Behavior
`Tuple` stores packed bytes in a standalone arena and element offsets in memory. It does not write to the database, but packed outputs are durable key material used by subspaces, directory-like layers, task buckets, and system-key encodings.

## Dependencies and Integration Points
It depends on Flow types, `FDBTypes`, and `TupleVersionstamp`. It integrates with C++ tuple users, Java binding tests conceptually, subspace APIs, task parameter codecs, and any code requiring lexicographically ordered composite keys.

## Risks and Edge Cases
Tuple encoding compatibility is critical because packed bytes become database keys. Incomplete numeric tuple parsing is optionally filtered, and callers must choose the right behavior for range scans. User type decoding can be excluded unless explicitly requested. `clear` replaces the standalone buffer so previously returned packed strings remain valid.

## Test Signals
Tuple round-trip tests, cross-binding tuple compatibility tests, key ordering tests, versionstamp tuple tests, incomplete tuple parsing tests, and subspace range tests are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Tuple.h -->
