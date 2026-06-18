# sources/storage-engines/foundationdb/bindings/c/foundationdb/fdb_c.h

## Purpose
`fdb_c.h` is the public FoundationDB C API header. It defines API-version selection macros, public structs and opaque handles, exported function declarations, compatibility gates for legacy APIs, key selector helper macros, and removed-function compile-time traps.

## Important APIs, Types, And Functions
- API macros require `FDB_API_VERSION` or `FDB_USE_LATEST_API_VERSION`/`FDB_USE_LATEST_BINDINGS_API_VERSION` and reject versions below 13 or above the generated latest version.
- `fdb_select_api_version(v)` and `fdb_select_api_version_capped(v)` wrap `fdb_select_api_version_impl`.
- Core structs include `FDBKey`, `FDBKeyValue`, `FDBKeySelector`, `FDBGetRangeReqAndResult`, `FDBMappedKeyValue`, `FDBKeyRange`, blob-granule compatibility structs, and `FDBTenant`.
- Future/result APIs include destroy/cancel/block/callback and typed result extractors.
- Database APIs include create/destroy/set option/create transaction, status/protocol/admin operations, and removed tenant stubs.
- Transaction APIs include get/getKey/getRange/mapped range, mutations, watch, commit, metrics/cost futures, versionstamp, on_error, reset, conflict ranges, estimated size, and split points.
- Legacy API blocks expose pre-610 cluster APIs, pre-23 future error APIs, and pre-14 transaction variants only when the selected API version allows them.

## Control Flow
This header controls compile-time visibility based on `FDB_API_VERSION`. Removed functions expand to an intentionally invalid macro so accidental calls fail at compile time. Runtime API selection still flows through `fdb_select_api_version_impl()` implemented in `fdb_c.cpp`.

## State And Persistence Behavior
The header documents pointer-lifetime and struct-layout contracts but owns no state. Returned pointers from future getters refer to future-owned memory. Transaction/database functions mutate FoundationDB state through the implementation library.

## Dependencies And Integration Points
It includes generated `fdb_c_apiversion.g.h`, generated `fdb_c_options.g.h`, and `fdb_c_types.h`. It is installed for external clients and is consumed by language bindings, C/C++ tests, and application code.

## Risks And Edge Cases
ABI layout is critical, especially packed `FDBKeyValue` and compatibility structures that mirror C++ internals. Some blob granule and tenant-related structs remain despite feature removal for compatibility. Consumers must select an API version exactly once before using the API. Compile-time API gates must stay synchronized with implementation-side function pointer changes.

## Test Signals
The C90 test verifies broad C compatibility. Unit/API/shim/upgrade tests exercise function declarations and runtime compatibility. Static assertions in `fdb_c.cpp` backstop selected layout assumptions.
