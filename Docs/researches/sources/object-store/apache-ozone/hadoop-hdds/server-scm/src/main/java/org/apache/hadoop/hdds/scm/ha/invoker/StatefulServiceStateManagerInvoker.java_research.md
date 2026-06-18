# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/StatefulServiceStateManagerInvoker.java

Purpose: Generated HA invoker for replicated `StatefulServiceStateManager` save/delete operations.

Important APIs and types: `ReplicateMethod` includes `deleteConfiguration(String)` and `saveConfiguration(String, ByteString)`. Proxy read and reinitialize paths are local; save/delete use `invokeReplicateDirect`.

Control flow: Proxy save/delete submit direct Ratis requests. Local apply casts service name and protobuf `ByteString`, invokes the real manager, and returns empty responses for void operations. Reads return local bytes.

State and persistence behavior: The invoker has no state beyond its implementation and Ratis server. Underlying manager persists bytes in the `statefulServiceConfig` table.

Dependencies and integration points: Used by `StatefulServiceStateManagerImpl.Builder`, `StatefulService`, and checkpoint reload paths.

Risks and test signals: ByteString codec must distinguish shaded Ratis `ByteString` from non-shaded protobuf `ByteString`. Tests should cover save/read/delete round trip through proxy, reinitialize pass-through, and method-not-found handling.
