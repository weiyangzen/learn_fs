# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/StatefulServiceStateManagerImpl.java

Purpose: Concrete state manager that stores service configuration bytes in a RocksDB table through the SCM DB transaction buffer and exposes a Ratis proxy.

Important APIs and types: Implements `saveConfiguration`, `readConfiguration`, `deleteConfiguration`, `reinitialize`, and `newBuilder`. Builder requires stateful-service table, transaction buffer, and Ratis server, then returns a proxy from `StatefulServiceStateManagerInvoker`.

Control flow: Save enqueues a table put in the transaction buffer and immediately flushes when the buffer is an `SCMHADBTransactionBuffer`. Read fetches the table value. Delete currently calls `statefulServiceConfig.delete` directly. Reinitialize replaces the table reference.

State and persistence behavior: Owns a mutable table reference plus a transaction buffer. Save is buffered and flushed; delete bypasses the transaction buffer in this implementation, which is an important persistence-path distinction.

Dependencies and integration points: Used by SCM services through `StatefulService`; reloaded by `SCMHAManagerImpl.startServices` after checkpoint install.

Risks and test signals: Direct delete may bypass HA transaction metadata unlike save. Tests should cover builder null validation, save flush behavior, delete replication/local persistence, read after reinitialize, and generated proxy routing.
