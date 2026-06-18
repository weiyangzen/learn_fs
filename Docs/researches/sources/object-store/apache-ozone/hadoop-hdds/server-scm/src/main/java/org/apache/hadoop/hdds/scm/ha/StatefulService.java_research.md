# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/StatefulService.java

Purpose: Abstract base for SCM services that need replicated, RocksDB-backed configuration bytes.

Important APIs and types: Parameterized by protobuf message type `CONF`. Constructor accepts `StatefulServiceStateManager` and a protobuf `Parser<CONF>`. Protected final helpers are `saveConfiguration`, `readConfiguration`, and `deleteConfiguration`; `getServiceName` returns the class simple name.

Control flow: Subclasses call save/read/delete helpers; the manager keys persisted configuration by the service name. Reads return null when no bytes exist and otherwise parse the stored `ByteString`.

State and persistence behavior: Runtime state is service name, state manager, and parser. Durable state is the `statefulServiceConfig` table entry keyed by service name.

Dependencies and integration points: Used by background services that implement `SCMService` and need HA-replicated configuration.

Risks and test signals: Class-simple-name keys can collide after refactors or subclass renames, so compatibility matters. Tests should cover save/read/delete round trips, parse failures, null reads, and that subclass service names are stable.
