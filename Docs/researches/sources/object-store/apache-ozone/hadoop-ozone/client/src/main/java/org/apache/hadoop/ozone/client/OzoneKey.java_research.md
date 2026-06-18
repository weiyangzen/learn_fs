## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneKey.java

### Purpose
`OzoneKey` is a client-visible value object for key metadata: volume, bucket, key name, owner, size, timestamps, replication config, metadata, tags, and whether the key represents a file.

### Important APIs and Types
Constructors accept primitive key fields and optionally metadata/tags. Getters expose all fields. Deprecated `getReplicationType` and `getReplicationFactor` adapt `ReplicationConfig` to legacy client APIs. `fromKeyInfo` converts OM `OmKeyInfo` into `OzoneKey`.

### Control Flow
Construction converts epoch-millis timestamps to `Instant`, stores final identity fields, and copies metadata/tags into mutable internal maps. `fromKeyInfo` pulls all public fields from OM key info.

### State and Persistence Behavior
This is an in-memory DTO. Metadata and tags maps returned by getters are mutable, so callers can alter local object state after construction. No changes persist to OM unless passed through separate APIs.

### Dependencies and Integration Points
It depends on HDDS `ReplicationConfig`, legacy replication types, Jackson `JsonIgnore` for deprecated compatibility getters, and OM `OmKeyInfo`. It is returned by `OzoneBucket.headObject`, list-key paths, and conversion helpers.

### Risks and Edge Cases
Mutable metadata/tag getters can surprise callers expecting immutable DTO behavior. Deprecated replication getters assume `replicationConfig` is non-null. Consumers should prefer `getReplicationConfig`.

### Test Signals
Tests should verify `fromKeyInfo` conversion, metadata/tag copying, legacy replication getter behavior for replicated and EC configs, and JSON serialization exclusion of deprecated getters.
