<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancer.java

## Purpose
SCM service wrapper for the container balancer. It persists desired run state/configuration, starts and stops the asynchronous balancing task, reacts to leader and safe-mode status changes, validates configuration, and exposes status/metrics.

## Important APIs, Types, And Functions
`ContainerBalancer` extends `StatefulService<ContainerBalancerConfigurationProto>`. Important methods are `notifyStatusChanged`, `shouldRun`, `isBalancerRunning`, `getBalancerStatusInfo`, `start`, `startBalancer`, `stop`, `stopBalancer`, `saveConfiguration`, `validateConfiguration`, and `validateNodeList`. It owns `ContainerBalancerTask`, `ContainerBalancerConfiguration`, `ContainerBalancerMetrics`, the current balancing thread, a lock, and start time.

## Control Flow
On SCM status changes, the service stops if the SCM is no longer leader or enters safe mode, and starts if leader/out-of-safe-mode and persisted `shouldRun` is true. CLI/service start validates leader readiness and safe mode, reads persisted config, validates it, and starts a daemon `ContainerBalancerTask` with optional safe-mode-exit delay. Manual start saves config with `shouldRun=true`. Stop either stops the local task or persists `shouldRun=false` for an operator stop, then joins the task thread while repeatedly interrupting it.

## State And Persistence
Persistent service state is a `ContainerBalancerConfigurationProto` with `shouldRun` and `nextIterationIndex`, stored through `StatefulService`. Runtime state includes the active task, thread, metrics source, lock, start timestamp, and current config.

## Dependencies And Integration Points
Depends on `StorageContainerManager`, `SCMContext`, SCM service manager registration, stateful service state manager, Ozone configuration, DU refresh config, SCM node manager for include/exclude validation, and `ContainerBalancerTask`.

## Risks And Test Signals
Start/stop is lock-protected but thread join intentionally occurs outside the lock. Persisted config must be present for service auto-start; missing config means no run. Configuration validation enforces move timeout relationships and source/target size limits but only warns when balancing interval is shorter than DU refresh. Tests should cover leader/safe-mode transitions, persisted `shouldRun`, restart from next iteration, invalid node lists, invalid size and timeout configs, stop persistence, task thread lifecycle, and status proto conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancer.java -->
