# sources/test-tools/stress-ng/core-hash.h

## Purpose

This header defines the public non-cryptographic hash and hash-table API for stress-ng.

## Important APIs, Types, And Functions

`stress_hash_t` is a minimal linked-list node used as the base of stored hash entries. `stress_hash_table_t` owns a bucket array and the bucket count. The header declares table creation/add/get/delete plus all exported 32-bit hash functions.

## Control Flow

The table API is intentionally opaque enough that callers do not need to know bucket layout, but exposed enough that `stress_hash_t` can be embedded or inspected as a linked list node. Hash functions are standalone utilities.

## State And Persistence Behavior

The table object returned by `stress_hash_create` owns heap memory and must be released with `stress_hash_delete`. Hash function calls have no persistent state.

## Dependencies And Integration Points

The header includes `core-attribute.h` for annotations such as `WARN_UNUSED`. It is included by filesystem and helper code and by stressors needing named hash algorithms.

## Risks And Test Signals

API changes affect broad utility code. Compile tests should verify prototypes match implementation, and runtime tests should verify table ownership and duplicate insertion semantics.
