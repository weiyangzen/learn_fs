# sources/sync-backup/casync/src/hash-funcs.h

## Purpose

`hash-funcs.h` declares the hash operation interface used by `hashmap.c` and predefined hash/comparison implementations.

## Important APIs, Types, and Functions

It defines `hash_func_t`, `compare_func_t`, and `struct hash_ops` with `.hash` and `.compare` callbacks. It declares string, trivial pointer, and `uint64_t` hash/compare functions plus their exported `hash_ops` instances. Attributes mark compare functions as pure/const where appropriate.

## Control Flow

The hashmap implementation initializes siphash state and calls the `.hash` callback, then uses `.compare` when scanning candidate buckets.

## State and Persistence Behavior

The header has no state. The external `hash_ops` objects are immutable.

## Dependencies and Integration Points

It includes `util.h` for attributes/macros and `siphash24.h` for the hash state type. `hashmap.h` includes this header to let callers choose key behavior.

## Risks and Edge Cases

Callers must select hash ops that match key ownership and representation. Using `trivial_hash_ops` for strings or `string_hash_ops` for non-NUL data will produce incorrect behavior or memory errors.

## Test Signals

Compile tests should verify callback signatures and const/pure attributes; runtime tests should use each ops object in maps and sets with representative keys.
