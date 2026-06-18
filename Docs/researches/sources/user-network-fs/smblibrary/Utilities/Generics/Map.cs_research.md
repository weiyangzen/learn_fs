# sources/user-network-fs/smblibrary/Utilities/Generics/Map.cs

Purpose: `Map<T1,T2>` implements a bidirectional one-to-one dictionary.

Important APIs/types/functions: `Add`, `ContainsKey`, `ContainsValue`, `TryGetKey`, `TryGetValue`, `RemoveKey`, `RemoveValue`, indexer by forward key, and `GetKey` by reverse value.

Control flow: `Add` inserts into both forward and reverse dictionaries; removals look up the opposite side and remove both entries; get methods delegate to the relevant dictionary.

State and persistence behavior: in-memory paired dictionaries only.

Dependencies and integration points: general utility for code needing reverse lookup.

Risks: `Add` is not transactional: if forward insert succeeds and reverse insert fails due to duplicate value, the map can become inconsistent. Null support depends on dictionary key types. No update method exists.

Test signals: duplicate key/value insertion, failed-add consistency, remove by key/value, reverse lookup, and missing-key exception behavior.
