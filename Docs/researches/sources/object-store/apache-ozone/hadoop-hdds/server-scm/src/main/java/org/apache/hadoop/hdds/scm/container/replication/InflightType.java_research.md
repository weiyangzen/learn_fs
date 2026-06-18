# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/InflightType.java

Purpose: `InflightType` is a package-private enum classifying pending replication-manager actions as `REPLICATION` or `DELETION`.

Important APIs and behavior: the enum has two values and no methods. Package-private visibility keeps it internal to `org.apache.hadoop.hdds.scm.container.replication`.

Control flow: no control flow exists here; consumers branch on the enum to distinguish add-like work from delete-like work.

State and persistence: enum values are JVM constants. This type itself has no persistence. Any persisted or timed behavior is owned by pending-operation trackers or command queues that store the classification.

Dependencies and integration: it has no imports. It is intended to be used by in-flight action maps, pending-operation logic, or legacy tracking code in the same package.

Risks: the enum names are broad; code that needs EC reconstruction versus Ratis replication, or push versus pull, must not rely on this type alone. Adding new action types would require auditing package-private switch statements and metrics.

Test signals: coverage is indirect through tests that verify pending replication and deletion accounting, such as `TestContainerReplicaPendingOps`, `TestUnderReplicatedProcessor`, and `TestOverReplicatedProcessor`.
