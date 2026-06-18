# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/StatefulServiceStateManager.java

Purpose: Replicated state manager API for saving, reading, deleting, and reinitializing `StatefulService` configuration entries.

Important APIs and types: `saveConfiguration` and `deleteConfiguration` are annotated `@Replicate`; `readConfiguration` is local read-only; `reinitialize` swaps in a new `Table<String, ByteString>`. Default `getType` returns `RequestType.STATEFUL_SERVICE_CONFIG`.

Control flow: Proxied implementations submit save/delete through Ratis so all SCMs apply the same table mutations. Reads fetch the local persisted bytes for the service name.

State and persistence behavior: Persists protobuf bytes in the `statefulServiceConfig` column family. Reinitialize points the manager at the table from a newly loaded SCM DB checkpoint.

Dependencies and integration points: Used by `StatefulService` and implemented by `StatefulServiceStateManagerImpl` with an invoker.

Risks and test signals: Save/delete consistency depends on generated invoker mapping and codec support for `ByteString`. Tests should cover replicated save/delete, local read, table swap after checkpoint install, and request type registration.
