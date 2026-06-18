## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ReplicationPolicy.h

Purpose: Declares the replication policy tree interface and concrete policy nodes that select/validate locality-aware replica sets.

Important APIs/types/functions: `IReplicationPolicy` defines `name()`, `info()`, `maxResults()`, `selectReplicas()`, `validate()`, `validateFull()`, tracing helpers, attribute-key collection, cached `depth()`/`maxdepth()`, and serialization. `PolicyOne` selects one entry. `PolicyAcross` selects `_count` groups across a given attribute and applies an embedded policy within each group. `PolicyAnd` composes multiple policies and sorts them for selection by max results/depth. `serializeReplicationPolicy()` writes a policy type name plus payload and reconstructs `One`, `Across`, `And`, or null. `dynamic_size_traits<Reference<IReplicationPolicy>>` supports variable-sized serialized policy values.

Control flow: Policy operations recurse down the policy tree. `Across` restricts available servers by attribute values, tracks used values and added results, and applies the embedded policy. `And` runs multiple policies and validates combined requirements. Serialization dispatches by string type name, then calls the concrete policy serializer.

State and persistence behavior: Policies are reference-counted and cache depth/max-depth lazily. Serialization is protocol-sensitive and explicitly warns that `ProtocolVersion::ReplicationPolicy` must be considered for changes. `PolicyAcross` has mutable temporary caches/vectors used during selection.

Dependencies and integration points: Depends on `ReplicationTypes.h`, `LocalitySet` forward declarations, Flow serialization, and `TraceEvent`. Used by storage team selection, recruitment, configuration, and replication validation tooling.

Risks: Adding or renaming policy types is a wire-format change. Cached `_depth`/`_maxdepth` can become stale if mutable policy trees are modified after use. `PolicyAcross::isSingleAcrossOverPolicyOne()` relies on dynamic_cast shape and max-depth. Selection temporary members make thread-safety/reentrancy assumptions important.

Test signals: Policy serialization compatibility, type-name dispatch, `One`/`Across`/`And` selection and validation, attribute-key collection, depth/maxdepth traversal, unavailable/insufficient locality cases, and full validation with `alsoServers`.
