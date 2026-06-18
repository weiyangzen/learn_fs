# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/AbstractDiskBalancerSubCommand.java

## Purpose
Provides the shared execution framework for datanode DiskBalancer subcommands across explicit datanode targets and batch `--in-service-datanodes` mode.

## Important APIs, Types, And Functions
It implements `Callable<Void>`, mixes in `DiskBalancerCommonOptions`, checks `HDDS_DATANODE_DISK_BALANCER_ENABLED_KEY`, resolves target datanodes, executes abstract `executeCommand(String)`, and delegates result display to `displayResults`. It also supplies `validateParameters`, `getActionName`, `getConfigurationMap`, JSON error result construction, and `formatDatanodeDisplayName`.

## Control Flow
`call()` verifies the feature flag, validates target selection, performs subclass validation, resolves targets from positional args or SCM's healthy IN_SERVICE datanodes, deduplicates, runs the command sequentially for each datanode, accumulates success/failure/JSON results, and emits either JSON or consolidated text.

## State And Persistence
It persists nothing locally. It caches batch display-name mappings and controls RPC fan-out to datanode DiskBalancer services.

## Dependencies And Integration Points
Depends on `ContainerOperationClient`, `DiskBalancerSubCommandUtil`, `JsonUtils`, Ozone config keys, and subclass RPC implementations.

## Risks And Test Signals
Errors generally print and return null rather than throwing, so shell exit status may not reflect validation failures. Batch execution is sequential and may be slow for large clusters. Tests should cover disabled feature flag, missing targets, batch target discovery, JSON success/failure arrays, duplicate targets, and subclass validation.
