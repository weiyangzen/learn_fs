# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMMXBean.java

Purpose: `SCMMXBean` is the JMX management interface for SCM runtime information. It extends `ServiceRuntimeInfo` with SCM-specific ports, IDs, safe mode state, container state, HA role, and storage directory information.

Important APIs and types: Methods expose datanode and client RPC ports, safe mode boolean and current container threshold, container state counts, safe mode rule statuses, SCM ID, cluster ID, Ratis roles, primordial node, Ratis log directory, RocksDB directory, and hostname.

Control flow: This is an interface with no implementation. `StorageContainerManager` or an adapter supplies the values for JMX and metrics sources such as `SCMContainerMetrics`.

State and persistence behavior: The interface owns no state. Implementations read from SCM context, storage config, managers, and runtime service metadata.

Dependencies and integration points: It is consumed by JMX tooling, metrics code, and operator diagnostics. It bridges internal SCM manager state to external observability.

Risks: Return types are loosely structured for some values, such as `Map<String, String[]>` for rule status and `List<List<String>>` for Ratis roles. Consumers must tolerate implementation-specific formatting.

Test signals: Implementation tests should assert stable values for ports, IDs, safe mode status, rule status formatting, container state counts, HA role lists, and directory paths.
