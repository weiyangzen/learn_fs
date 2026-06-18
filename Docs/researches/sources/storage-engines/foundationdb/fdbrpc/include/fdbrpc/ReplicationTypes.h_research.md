## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ReplicationTypes.h

Purpose: Provides the compact integer-backed attribute, value, entry, and record structures that power locality replication maps and policies.

Important APIs/types/functions: `AttribKey`, `AttribValue`, and `LocalityEntry` are small ID wrappers with ordering/equality. `KeyValueMap` stores sorted `(AttribKey, AttribValue)` pairs and supports `getValue()` and `isPresent()` via binary search. `LocalityRecord` attaches a `KeyValueMap` to an entry index. `StringToIntMap` maps strings to stable-in-map integer IDs and supports reverse lookup, clear/copy, and memory accounting. `g_replicationdebug` and `emptyEntryArray` are externs used by replication code.

Control flow: `StringToIntMap::convertString()` assigns IDs incrementally. `KeyValueMap` queries use lower_bound with key or key/value comparators. `LocalityRecord` delegates queries to its map and can produce debug strings.

State and persistence behavior: These are in-memory helper structures; their integer IDs are local to a map/group and are not a global durable encoding. `StringToIntMap` owns the string-ID state used by `LocalityGroup`.

Dependencies and integration points: Depends on Flow types and `LocalityData`. Used by `Replication.h`, `ReplicationPolicy.h`, and replication utilities.

Risks: IDs are only meaningful within their owning maps; mixing keys/values from different groups can produce wrong answers. `lookupString()` returns `"<missing>"` for out-of-range IDs, which is useful for debug but can hide a caller bug. Correctness assumes `KeyValueMap` arrays are sorted before lookup.

Test signals: String-to-ID stability within a map, reverse lookup, sorted key/value lookup, absent-key behavior, memory accounting, and record debug formatting.
