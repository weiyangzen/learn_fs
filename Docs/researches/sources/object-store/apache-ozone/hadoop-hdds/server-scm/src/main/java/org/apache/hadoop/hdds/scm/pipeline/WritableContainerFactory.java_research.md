<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableContainerFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableContainerFactory.java

Purpose: `WritableContainerFactory` is the replication-type router for block allocation. It returns a writable `ContainerInfo` by delegating to Ratis/standalone or EC providers based on the requested `ReplicationConfig`.

Important APIs and types: The constructor wires providers from `StorageContainerManager`: `WritableRatisContainerProvider` for RATIS and STAND_ALONE, and `WritableECContainerProvider` for EC. `getContainer(long, ReplicationConfig, String, ExcludeList)` is the public dispatch method.

Control flow: Construction reads SCM configuration, creates the EC provider config object, calculates configured container size, and registers the EC config with the reconfiguration handler. `getContainer` switches on replication type and casts EC configs to `ECReplicationConfig`.

State and persistence behavior: The factory holds provider instances only. It does not persist containers or pipelines; delegated managers do. EC provider configuration is reconfigurable after registration.

Dependencies and integration points: It integrates block allocation with `PipelineManager`, `ContainerManager`, `NodeManager`, pipeline choose policies, `StorageContainerManager`, and dynamic reconfiguration.

Risks: STAND_ALONE currently shares the Ratis writable provider path, which is intentional but easy to misread. Invalid replication types fail with `IOException`. EC requests rely on the runtime type of `repConfig`.

Test signals: Tests should assert routing by replication type, invalid-type errors, EC config registration, configured container size propagation, and exclude-list forwarding to providers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableContainerFactory.java -->
