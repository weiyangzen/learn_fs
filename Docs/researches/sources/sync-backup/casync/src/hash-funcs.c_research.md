# sources/sync-backup/casync/src/hash-funcs.c

## Purpose

`hash-funcs.c` provides reusable hash and comparison operations for the local hashmap/set implementation: strings, pointer identity, and `uint64_t` values.

## Important APIs, Types, and Functions

`string_hash_func()` hashes the NUL-terminated string including the terminator; `string_compare_func()` uses `strcmp()`. `string_hash_ops` packages them. `trivial_hash_func()` hashes the pointer value itself by compressing the address variable; `trivial_compare_func()` orders pointer values directly. `trivial_hash_ops` packages pointer-identity behavior. `uint64_hash_func()` hashes eight bytes at the pointed-to value; `uint64_compare_func()` compares dereferenced `uint64_t` values; `uint64_hash_ops` packages them.

## Control Flow

Each hash function feeds data into an existing siphash state; each compare function returns the standard negative/zero/positive relation expected by `hashmap.c`.

## State and Persistence Behavior

No state is stored. Hash randomization state is owned by the hashmap implementation's siphash key.

## Dependencies and Integration Points

The file depends on `hash-funcs.h`, which includes `siphash24.h` and `util.h`. `hashmap.c`, `set.h`, and callers use these `hash_ops` objects to specialize key behavior.

## Risks and Edge Cases

String functions require valid NUL-terminated strings. Trivial pointer comparison uses relational operators on unrelated object pointers, which is common in system code but can be implementation-defined in strict C terms. `uint64_hash_func()` requires aligned enough memory for dereference in the compare function.

## Test Signals

Tests should verify equal strings/uint64 values collide to equal compare results, different values compare nonzero, trivial ops distinguish different pointer addresses, and hash ops work through `Hashmap` and `Set` insertion/lookup/removal.
