# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerStopSubcommand.java

## Purpose
Implements `ozone admin datanode diskbalancer stop`, stopping DiskBalancer on selected datanodes.

## Important APIs, Types, And Functions
Extends `AbstractDiskBalancerSubCommand`; `executeCommand` creates a `DiskBalancerProtocol` proxy, calls `stopDiskBalancer`, and returns a JSON success map with datanode/action/status.

## Control Flow
The base class resolves targets and calls this command for each. Text mode prints batch or explicit success/failure summaries; JSON mode output is handled by the base class.

## State And Persistence
It mutates datanode-local DiskBalancer running state by stopping the service/workflow.

## Dependencies And Integration Points
Depends on `DiskBalancerProtocol.stopDiskBalancer` and shared target/display handling.

## Risks And Test Signals
Stop failures are per-node and may still allow other nodes to be processed. Tests should cover already stopped service, unreachable node, JSON error result, batch all-success message, and proxy close.
