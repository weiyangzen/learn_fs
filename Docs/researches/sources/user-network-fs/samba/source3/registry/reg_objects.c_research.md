# sources/user-network-fs/samba/source3/registry/reg_objects.c

## Purpose
`reg_objects.c` implements the in-memory containers used to pass registry subkeys and values between backends, dispatchers, and callers.

## Important APIs, Types, And Functions
It defines private `struct regval_blob`, `struct regval_ctr`, and `struct regsubkey_ctr`. Subkey APIs include init, reinit, sequence-number accessors, add/delete/existence, count, and indexed lookup. Value APIs include init, count, accessors for name/type/data/size, indexed and name lookup, compose, add/copy/delete, `REG_SZ` and `REG_MULTI_SZ` helpers, and sequence-number accessors.

## Control Flow
Subkey initialization allocates a talloc-owned container and an in-memory dbwrap rbtree for case-insensitive key-name lookup. Adding a subkey skips null and duplicate names, grows the pointer array, duplicates the name, hashes it with its index, and increments the count. Deleting looks up the index, removes the hash entry, shifts the array, and rehashes shifted entries. Value addition deletes any existing value with the same name, grows the pointer array, composes a new blob, and appends it.

## State And Persistence
Containers are talloc-owned transient state. Sequence numbers allow callers to compare container freshness against backend database sequence numbers. The subkey hash is an in-memory rbtree, not persistent storage.

## Dependencies And Integration Points
The file depends on registry types, dbwrap rbtree, TDB utility helpers, `util_reg` push functions, and string wrappers. Backends populate these containers in their fetch methods; database code and RPC/frontends consume them.

## Risks And Test Signals
Memory ownership and error recovery are the main risks. `regval_ctr_addvalue()` resets `num_values` to zero on allocation failure, which can discard existing logical contents. Subkey deletion does not shrink/free removed string slots because talloc context ownership handles lifetime. Tests should cover case-insensitive subkey existence, duplicate suppression, deletion and rehashing, value replacement, zero-length values, long value-name truncation through `fstring`, sequence numbers, and allocation-failure behavior where possible.
