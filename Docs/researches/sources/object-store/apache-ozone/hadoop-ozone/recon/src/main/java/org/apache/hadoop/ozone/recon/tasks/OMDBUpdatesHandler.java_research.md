# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OMDBUpdatesHandler.java

Purpose: RocksDB write-batch handler that converts OM DB write operations into decoded `OMDBUpdateEvent` instances for Recon tasks.

Important APIs: constructor with `OMMetadataManager`, `setLatestSequenceNumber`, `getLatestSequenceNumber`, overridden `put` and `delete` with column-family index, `close`, and `getEvents`.

Control flow and state: `processEvent` maps column-family index to table name, retrieves the column-family definition, decodes key and value bytes, fetches old value either from the latest event map or OM table `getSkipCache`, validates events with `OmUpdateEventValidator`, and emits PUT, DELETE, or UPDATE. `omdbLatestUpdateEvents` tracks the latest event per table/key within the batch so multiple operations collapse old-value semantics correctly. Many RocksDB handler methods are intentionally no-op because Recon only needs put/delete.

Dependencies and integration: depends on OM DB definitions/codecs, `OMMetadataManager`, RocksDB `ManagedWriteBatch.Handler`, and `OmUpdateEventValidator`. Downstream `OMUpdateEventBatch` wraps the generated events for task processing.

Risks: unsupported merge/delete-range/single-delete operations would be ignored if OM began emitting them. DELETE without an old value is skipped, so missing local state can lose delete events. `close` clears the latest-event map but intentionally leaves event list available. Generic raw tables and decoded objects rely on validator coverage.

Test signals: cover PUT new key, PUT existing key as UPDATE, PUT after DELETE in same batch, DELETE old-value capture, validation skips, non-string key warning path, close behavior, and ignored operation types if OM usage changes.
