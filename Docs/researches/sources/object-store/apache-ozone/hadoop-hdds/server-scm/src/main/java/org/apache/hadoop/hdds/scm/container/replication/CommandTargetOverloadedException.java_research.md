# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/CommandTargetOverloadedException.java

Purpose: checked exception indicating that all possible command targets are overloaded.

Important APIs: message constructor extending `IOException`.

Control flow and state: pure exception type; no additional fields or behavior.

Dependencies and integration: thrown by replication scheduling paths when command load limits prevent selecting a target or source. Tests in `TestReplicationManager` assert overloaded target scenarios.

Risks: no cause constructor, so lower-level selection errors cannot be preserved directly. Test signals should assert callers distinguish overload from no suitable node and from leader failures.
