# sources/test-tools/kdevops/scripts/kconfig/hashtable.h

## Purpose
This header provides a tiny Linux-style hash table macro layer over `hlist_head` lists for Kconfig symbol lookup.

## Important APIs, Types, And Functions
Macros include `HASH_SIZE(name)`, `HASHTABLE_DECLARE(name, size)`, `HASHTABLE_DEFINE(name, size)`, `hash_head(table, key)`, `hash_add(table, node, key)`, `hash_for_each(table, obj, member)`, and `hash_for_each_possible(table, obj, member, key)`.

## Control Flow
All behavior expands inline at compile time. Insertion hashes a key modulo array size and prepends an hlist node. Iteration either walks all buckets or a single key bucket.

## State And Persistence
The table is caller-owned static or external memory. The macros mutate hlist links but have no persistence.

## Dependencies And Integration Points
It depends on `array_size.h` and `list.h`. `internal.h` uses it to declare `sym_hashtable` and `for_all_symbols()`.

## Risks And Test Signals
The hash function is only `key % size`; quality depends entirely on caller-provided keys. There is no deletion wrapper here. Macro arguments may be evaluated in ways callers must understand. Test by inserting known symbol structures and iterating all and bucket-local paths.
