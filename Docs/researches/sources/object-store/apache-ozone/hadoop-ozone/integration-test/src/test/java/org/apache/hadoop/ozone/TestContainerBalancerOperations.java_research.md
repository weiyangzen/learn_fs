# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestContainerBalancerOperations.java

Purpose: integration tests for SCM container balancer client operations exposed through `ContainerOperationClient`: start, stop, status, CLI-option/config precedence, include/exclude container parsing, and idempotent stop.

Important APIs/types/functions: `setup`, `cleanup`, `testContainerBalancerCLIOperations`, `testIfCBCLIOverridesConfigs`, `testStopBalancerIdempotent`, and `parseContainerIDs`. It uses `MiniOzoneCluster`, `ContainerOperationClient`, `ScmClient`, `ContainerBalancerConfiguration`, `SCMContainerPlacementCapacity`, and `ContainerID`.

Control flow: setup starts a 3-DN cluster with capacity placement policy, node report interval 5 seconds, and DU trigger before move enabled. The first test asserts balancer initially stopped, starts it with a full set of optional CLI values, verifies running, waits until it stops naturally, starts it again, then stops it explicitly. Config precedence test mutates `ozoneConf` values for iterations and max datanode percentage, starts with some optionals empty and others present, inspects the live balancer config from SCM, and asserts defaults, config values, and CLI overrides are selected correctly. Stop-idempotent test calls stop while already stopped, starts/stops, then calls stop again under `assertDoesNotThrow`.

State and persistence: live SCM container balancer state/config, cluster configuration, and balancer runtime thread status. No durable output beyond cluster metadata.

Dependencies and integration points: SCM CLI client, container balancer service, placement policy class binding, node reports/DU, optional CLI argument mapping, and `GenericTestUtils.waitFor`.

Risks: tests do not create intentional imbalance or assert actual move plans; they primarily validate command plumbing. Natural stop timing can depend on balancer internals and cluster state. Shared static `ozoneConf` and client across tests means config mutations can persist within the class.

Test signals: balancer status false/true/false transitions, no exception from idempotent stop, and exact config values for balancing interval, iterations, max datanode percentage, excluded containers, and included containers.
