# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMDBUpdateEvent.java

Purpose: Immutable data carrier for one OM RocksDB update event consumed by Recon tasks.

Important APIs/types: getters for action, table, key, value, old value, and sequence number; nested `OMUpdateEventBuilder`; and enum `OMDBUpdateAction` with PUT, DELETE, UPDATE.

State and persistence: no persistence. It transports decoded key/value objects and the batch sequence number from `OMDBUpdatesHandler` to `ReconOmTask` processors.

Dependencies and integration: built by `OMDBUpdatesHandler` after decoding RocksDB write batch entries with OM DB codecs. Consumed by container-key, file-size, namespace summary, and insight tasks.

Risks: builder setters are package-private raw-style methods, so type safety is limited inside the package. `equals` and `hashCode` ignore value, old value, and sequence number; this is suitable for de-dup by key/table/action but not full event identity. `equals` assumes updatedKey/table/action are non-null.

Test signals: cover builder output, equality semantics, sequence number propagation, and consumer handling for each action type.
