## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Replication.h

Purpose: Defines locality-indexed sets and maps used by replication policies to select and validate replicas across zones, racks, datacenters, and other locality attributes.

Important APIs/types/functions: `LocalitySet` holds entries plus per-set string-to-int key maps, value arrays, mutable entry arrays, and cached restricted subsets. It exposes `selectReplicas()`, `validate()`, `restrict()`, `getMatches()`, random selection helpers, key/value conversion/text helpers, memory accounting, copy/deep-copy, and cache reporting. `LocalityGroup` is the root set containing `LocalityRecord` objects and the shared value map. `LocalityMap<V>` extends `LocalityGroup` to associate entries with external objects and return selected object pointers.

Control flow: Adding locality data converts string attributes to sorted integer records and updates key/value indexes. Restricting by attribute uses `_cacheArray` when possible; otherwise it scans entries, maps local keys to group keys, builds a derived `LocalitySet`, and caches it. Replica selection delegates to an `IReplicationPolicy`, passing a reference-counted set and accumulating `LocalityEntry` results. `LocalityMap` then maps selected entries back to object pointers.

State and persistence behavior: State is in-memory and reference-counted. Copy can share maps/records, while deep-copy duplicates key/value maps and makes the new set its own locality group. There is no direct serialization here, but it consumes serializable `LocalityData` and policy trees.

Dependencies and integration points: Depends on `Locality.h`, `ReplicationPolicy.h`, and `ReplicationTypes.h`. Higher-level storage recruitment and team-building code uses these structures to enforce fault-domain placement policies.

Risks: The cache stores derived `LocalitySet` references and must be cleared whenever entries or key maps change. Copy vs deep-copy semantics are subtle because `_localitygroup`, `_keymap`, and `_valuemap` may be shared. Random selection mutates `_mutableEntryArray`, so repeated selection behavior depends on prior calls. Attribute names must match policy expectations exactly.

Test signals: Add/restrict/cache hit/miss behavior, policy selection on root and derived sets, copy/deep-copy independence, random exception selection, object mapping in `LocalityMap`, memory accounting, and cache invalidation after clear/add.
