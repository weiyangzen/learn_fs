# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationTask.java

Purpose: concrete replication task created from an SCM `ReplicateContainerCommand`.

Important APIs and functions: the main constructor extracts container ID, deadline, term, priority, sources, target, and debug string from the command, and allows execution on out-of-service datanodes when the command has a target, which identifies push replication. `equals` and `hashCode` deduplicate by container ID and target. `runTask` delegates to the injected `ContainerReplicator`. Accessors expose sources, transferred bytes, metric name/description, and target.

Control flow and state: transferred bytes are mutable and appended to `toString` once positive. Pull tasks usually have sources only; push tasks have a target and relaxed in-service restriction.

Dependencies and integration: scheduled by `ReplicationSupervisor` and executed by pull/push replicator implementations. The command object is from `org.apache.hadoop.ozone.protocol.commands`.

Risks and test signals: deduplication treats pull replications of the same container as equal because target is null, but allows separate target-specific push tasks. Tests should cover equality semantics, out-of-service flag for target commands, transferred byte logging, metric names, and delegate invocation.
