<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TupleVersionstamp.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TupleVersionstamp.h

## Purpose
`TupleVersionstamp.h` declares the 12-byte tuple versionstamp wrapper used by tuple encoding for incomplete and complete FoundationDB versionstamps.

## Important APIs, Types, and Functions
The file defines `VERSIONSTAMP_TUPLE_SIZE`, `TupleVersionstamp::DEFAULT_VERSIONSTAMP`, constructors from default, `StringRef`, and `(version, batchNumber, userVersion)`, plus `getVersion`, `getBatchNumber`, `getUserVersion`, `size`, `begin`, and equality.

## Control Flow
Callers construct a versionstamp either from raw bytes or from structured version, batch, and user version fields. Tuple code appends the bytes and later decodes fields through getters. The default value is the incomplete versionstamp marker with invalid version bytes and zero batch/user version.

## State and Persistence Behavior
The type stores a standalone 12-byte string. It does not persist independently, but packed tuple keys containing versionstamps are written by versionstamped operations and resolved at commit time.

## Dependencies and Integration Points
It depends on Flow arenas and is consumed by `Tuple.h`, transaction versionstamp APIs, tuple layer code, and binding compatibility tests.

## Risks and Edge Cases
Raw `StringRef` construction must enforce or assume 12-byte input in the implementation. Signed getter return types for batch and user version require care around values above signed range. Versionstamp encoding must stay cross-language compatible.

## Test Signals
Signals include tuple versionstamp pack/unpack tests, versionstamped key commit tests, and cross-binding tuple compatibility tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TupleVersionstamp.h -->
