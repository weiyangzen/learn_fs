# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DecommissionStatusSubCommand.java

## Purpose
Implements `ozone admin datanode status decommission`, showing progress and container details for nodes currently in DECOMMISSIONING.

## Important APIs, Types, And Functions
Options include `--json` and `NodeSelectionMixin`. It queries `ScmClient.queryNode(DECOMMISSIONING, ...)`, filters through `DecommissionUtils.getDecommissioningNodesList`, reads JMX metrics with `getMetrics`, derives counts with `DecommissionUtils.getCountsMap`, and fetches `getContainersOnDecomNode`.

## Control Flow
The command rejects `--hostname`, filters decommissioning nodes by node ID or IP when supplied, handles empty matches with stderr messages, gets NodeDecommissionMetrics JSON, then prints either JSON maps containing datanode details/metrics/containers or text sections per datanode.

## State And Persistence
Read-only against SCM node state, metrics, and container mappings.

## Dependencies And Integration Points
Depends on `DecommissionUtils`, `DatanodeDetails`, `ContainerID`, `JsonUtils`, SCM node query and metrics APIs, and `NodeSelectionMixin`.

## Risks And Test Signals
Metrics may be unavailable or mismatched to nodes; the command prints generic metric errors and continues. Tests should cover no decommissioning nodes, ID/IP filters, unsupported hostname, missing metrics JSON, container map output, and JSON conversion of container IDs.
