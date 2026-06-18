## sources/storage-engines/rocksdb/table/block_based/block_type.h

Purpose: defines `BlockType`, the compact enum identifying block-based table block roles, plus a string conversion helper for diagnostics.

Important APIs/types: `enum class BlockType : uint8_t` includes data, filter, filter partition index, properties, compression dictionary, range deletion, hash-index prefixes, hash-index metadata, meta index, index, user-defined index, and invalid. `BlockTypeToString()` maps each enum value to a stable human-readable string.

Control flow: there is no runtime stateful flow; call sites use the enum to select typed cache helpers, block roles, tracing/accounting labels, and format-specific parsing paths. `kInvalid` is explicitly required to stay last because arrays in cache code size themselves using it.

State and persistence behavior: the enum can represent persisted or cached block role metadata indirectly, but this header itself stores no state. Ordering is part of the ABI-like contract for helper arrays in `block_cache.cc`.

Dependencies/integration points: included by block cache and table-reader code. `Block_k*` wrappers in `block_cache.h` each advertise one `BlockType`, and `GetCacheItemHelper()` indexes arrays using these enum ordinal values.

Risks: adding or reordering values without updating helper arrays and string conversion can break cache helper selection. Missing `BlockTypeToString()` cases would degrade diagnostics.

Test signals: cache helper and table reader tests indirectly depend on correct mapping. No direct unit test for `BlockTypeToString()` appears in this file set.
