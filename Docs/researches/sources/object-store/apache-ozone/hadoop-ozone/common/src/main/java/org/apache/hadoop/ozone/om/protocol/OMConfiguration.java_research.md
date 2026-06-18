<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMConfiguration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMConfiguration.java

## Purpose

`OMConfiguration` is a transfer object for OM HA configuration, separating nodes currently in memory from nodes reloaded from the latest on-disk configuration.

## Important APIs, Types, And Functions

The nested `Builder` adds nodes to in-memory and new-config lists. Public methods are `getCurrentPeerList`, `getActiveOmNodesInNewConf`, and `getDecommissionedNodesInNewConf`.

## Control Flow, State, And Persistence

The constructor copies supplied node lists into internal lists. Query methods stream over those lists, returning current peer node IDs, active reloaded nodes, and decommissioned reloaded nodes. It does not store OM configuration itself; it transports snapshots through `OMAdminProtocol`.

## Dependencies And Integration Points

It depends on HDDS `NodeDetails` and OM `OMNodeDetails`. It is returned by admin protocol implementations and consumed by CLI/admin workflows for OM decommissioning and configuration reload checks.

## Risks And Test Signals

Duplicate node IDs are resolved by keeping the later stream value in map collectors. Tests should cover empty configs, duplicate node IDs, decommissioned filtering, current peer list excluding decommissioned in-memory nodes by construction, and builder copy isolation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMConfiguration.java -->
