# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/simple_maintenance.json

Purpose: This fixture verifies replication-manager behavior for containers with datanodes entering maintenance, including when configured maintenance redundancy is sufficient and when extra replication is required.

Important APIs and types: It defines Ratis and EC closed-container scenarios with `operationalState` ENTERING_MAINTENANCE. Scenario-specific knobs include `ratisMaintenanceMinimum` and `ecMaintenanceRedundancy`. Expected commands are either absent or `replicateContainerCommand`.

Control flow: The harness applies the maintenance redundancy settings, builds replica sets with maintenance nodes, runs replication checks, and compares expected under-replication counters and command lists. The first two scenarios allow maintenance without commands; the latter two require one Ratis replicate command or two EC replicate commands.

State and persistence behavior: Static test data only. It models how SCM computes effective replication while nodes are transitioning into maintenance.

Dependencies and integration points: The resource is coupled to replication-manager maintenance redundancy logic, Ratis versus EC command counts, and the JSON fixture loader.

Risks: It uses simple topologies and does not include unhealthy or stale replicas. Changes to default maintenance policy or command batching can require fixture updates.

Test signals: Empty expectations and no commands when maintenance redundancy is adequate; under-replication counters and expected replicate command counts when the redundancy knobs require extra copies.
