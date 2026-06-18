## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/ReplicationOptions.java

Purpose: shared parser and resolver for Ozone replication configuration options.

Important APIs and control flow: subclasses attach picocli options to protected setters. `fromParams` returns empty if neither type nor replication was supplied; for RATIS with no replication value it falls back to configured/default replication; otherwise it calls `ReplicationConfig.parseWithoutFallback`. `fromConfig` reads default type and replication from configuration and validates through `OzoneClientUtils`. `fromParamsOrConfig` chooses explicit parameters first. `setType` rejects unsupported `CHAINED` and `STAND_ALONE` and produces a user-facing error listing RATIS and EC.

State and dependencies: stores parsed type and replication strings in memory. Depends on `ReplicationConfig`, `ReplicationType`, Ozone config keys, and client validation helpers.

Risks and test signals: EC syntax and config fallback are sensitive; invalid values should fail before RPC. Consumers include bucket create and set replication config handlers.
