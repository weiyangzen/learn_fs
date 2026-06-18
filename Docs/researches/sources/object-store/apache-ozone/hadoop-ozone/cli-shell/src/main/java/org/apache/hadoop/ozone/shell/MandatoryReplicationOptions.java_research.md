## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/MandatoryReplicationOptions.java

Purpose: replication-option specialization requiring both replication type and replication definition.

Important APIs and control flow: overrides `setReplication` and `setType` from `ReplicationOptions` only to attach required picocli options. Parsing still delegates validation and conversion to the base class.

State and dependencies: stores parsed values in inherited fields. Depends on `ReplicationOptions` and picocli option injection.

Risks and test signals: useful for commands where falling back to config would be ambiguous. Invalid type handling is inherited. No direct tests in this subset.
