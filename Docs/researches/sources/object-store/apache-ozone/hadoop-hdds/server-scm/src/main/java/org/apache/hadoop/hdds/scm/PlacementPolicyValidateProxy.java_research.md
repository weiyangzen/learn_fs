# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/PlacementPolicyValidateProxy.java

Purpose: Routes placement validation to default or EC placement policy based on a container's replication type.

Important APIs and types: Constructor accepts default and EC `PlacementPolicy`; `validateContainerPlacement` takes replica datanodes and `ContainerInfo`.

Control flow: EC containers use `ecPlacementPolicy`; all other replication types use the default policy, passing required node count from the container's replication config.

State and persistence behavior: Stores policy references only; no persistence.

Dependencies and integration points: Centralizes validation routing for callers that handle both EC and replicated containers.

Risks: Null policies are unchecked. New replication types default to the non-EC policy unless the switch is updated.

Test signals: Tests should verify EC routing, default routing, and required-node propagation.
