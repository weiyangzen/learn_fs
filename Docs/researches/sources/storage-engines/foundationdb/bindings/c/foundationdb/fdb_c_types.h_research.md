# sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c_types.h

## Purpose
`fdb_c_types.h` defines the minimal opaque handle and scalar typedefs shared by public and internal C API headers.

## Important APIs, Types, And Functions
- Opaque structs: `FDBFuture`, `FDBResult`, `FDBCluster`, `FDBDatabase`, and `FDBTransaction`.
- Scalar aliases: `fdb_error_t` and `fdb_bool_t`, both `int`.
- `DLLEXPORT` guard and `extern "C"` wrapping for C++ consumers.

## Control Flow
There is no control flow; this header centralizes type declarations so other headers can refer to opaque API handles without including the full public API.

## State And Persistence Behavior
The opaque types represent runtime objects managed by `fdb_c.cpp`; this header owns no state.

## Dependencies And Integration Points
It is included by `fdb_c.h` and `fdb_c_internal.h`, and is installed as part of the C client headers.

## Risks And Edge Cases
Changing scalar typedef widths or opaque type names would break ABI/source compatibility. `FDBCluster` remains declared for legacy compatibility even though cluster APIs are removed for newer API versions.

## Test Signals
Compile coverage from all C API consumers and the C90 test validates that these declarations remain compatible.
