# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancer.java

## Purpose
`TestContainerBalancer` validates the service-level `ContainerBalancer` wrapper: start/stop state transitions, persisted run configuration, SCM leadership notifications, delayed restart behavior, configuration validation, status reporting, and validation of include/exclude node hostnames.

## Important APIs, Types, and Functions
The suite targets `ContainerBalancer`, `ContainerBalancerTask.Status`, `ContainerBalancerConfiguration`, `ContainerBalancerStatusInfo`, `IllegalContainerBalancerStateException`, and `InvalidContainerBalancerConfigurationException`. The fixture mocks `StorageContainerManager`, `NodeManager`, `MoveManager`, `SCMServiceManager`, and `StatefulServiceStateManager`, with an in-memory `serviceToConfigMap` for configuration persistence.

## Control Flow and State Behavior
`setup()` configures short SCM wait and node-report intervals, enables DU triggering, stores balancer configuration in `OzoneConfiguration`, wires SCM getters, and constructs `ContainerBalancer`. `testShouldRun` proves the persisted enable flag controls `shouldRun`. `testStartBalancerStop` verifies idempotent stop, rejects duplicate starts, and confirms RUNNING then STOPPED status. `testStartStopSCMCalls` exercises the service `start()` and `stop()` paths after persisted configuration says the balancer should run.

Leadership behavior is covered by `testNotifyStateChangeStopStart`: when `SCMContext` loses leadership the running balancer stops; when leadership returns and is marked ready, `notifyStatusChanged` restarts it. `testDelayedStartOnSCMStatusChange` captures logs and waits for the balancing thread to enter `TIMED_WAITING`, proving restart honors `hdds.scm.wait.time.after.safemode.exit`.

Configuration validation asserts move replication timeout must be less than move timeout and must leave enough datanode offset slack. Invalid include/exclude node names are rejected using `NodeManager.getNodesByAddress`, while valid hosts allow start. `testGetBalancerStatusInfo` checks that status info reflects explicitly configured threshold, iteration count, and DU trigger flag.

## Dependencies and Integration Points
The file integrates balancer service lifecycle with SCM HA context, stateful service configuration storage, host resolution through `NodeManager`, and logging. It does not depend on a real cluster or container placement.

## Risks and Test Signals
Risks covered include duplicate balancer threads, stale persisted run flags, incorrect behavior during SCM leadership changes, invalid timeout settings, and silent acceptance of bad node filters. Signals include status enum assertions, exception assertions, log capture, and status-info field comparisons.
