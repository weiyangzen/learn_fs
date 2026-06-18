# sources/storage-engines/wiredtiger/test/cppsuite/src/main/validator.h

## Purpose
Declares the default validation algorithm and supporting data structures for replaying tracked operations.

## Important APIs, Types, And Functions
`key_state` stores expected existence and value. `validation_collection` aliases `std::map<key_value_t, key_state>`. `validator::validate` is public; helper methods for schema parsing, model updates, collection/file verification, and key/value verification are private.

## Control Flow
The public API receives operation tracker table name, schema tracker table name, and the in-memory `database` model. Private helpers reconstruct expected state and compare it to on-disk records.

## State And Persistence Behavior
`validator` itself is stateless. Temporary maps model expected collection contents during validation.

## Dependencies And Integration Points
Includes `database.h` for collection names and key/value type aliases. Used by `database_operation.cpp` as the default validation backend.

## Risks And Test Signals
Validation is designed for the default operation tracker schema only. The map is sorted by key, which aligns with deterministic verification but may become memory-heavy for very large tracked workloads.
