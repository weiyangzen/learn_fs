# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/ozone/audit/SCMAction.java

Purpose: `SCMAction` enumerates SCM audit action names. Protocol servers and SCM admin/client handlers use these constants to record auditable operations with consistent action strings.

Important APIs and types: The enum implements `AuditAction` and defines action constants for datanode registration/heartbeat, SCM info, block/container allocation and deletion, pipeline operations, safe mode, replication manager, container balancer, SCM HA actions, upgrade finalization, datanode usage, token retrieval, metrics, node queries, reconciliation, deleted-block summaries, and container suppression. `getAction` returns `toString()`.

Control flow: There is no internal branching. Audit code selects an enum value at call sites and calls `getAction` when emitting audit records.

State and persistence behavior: The enum is static process state. Audit records generated elsewhere may persist or ship the returned names, so enum names are externally visible compatibility strings.

Dependencies and integration points: It integrates SCM protocol implementations with the common Ozone audit framework. Adding a new audited SCM operation generally requires adding a new constant and using it in the corresponding server method.

Risks: Renaming or removing enum constants changes audit log action strings and can break downstream parsing. `getAction` returning `toString` means there is no stable alias separate from the Java name. The enum has no grouping or metadata, so read/write/admin semantics must be encoded by call sites.

Test signals: Tests should verify new SCM operations use an appropriate action and that expected audit action strings remain stable for log consumers.
