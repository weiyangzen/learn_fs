# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/TopologySubcommand.java

## Purpose
Implements `ozone admin printTopology`, displaying SCM's datanode network topology in text or JSON with optional ordering and state filtering.

## Important APIs, Types, And Functions
Options include `--order`, `--full`, `--operational-state`, `--node-state`, and `--json`. It queries `ScmClient.queryNode` for `HEALTHY`, `STALE`, and `DEAD`, filters operational and health states, and formats via `printOrderedByLocation`, `printNodesWithLocation`, `formatPortOutput`, and nested JSON DTOs `NodeTopologyOrder`, `NodeTopologyDefault`, and `NodeTopologyFull`.

## Control Flow
For each node state, the command queries SCM cluster-wide, applies optional string-validated filters, then prints either by network location or by node list. JSON mode serializes DTO collections through `JsonUtils`; text mode prints state headings and datanode address/port/operational data.

## State And Persistence
No state is persisted. Runtime state is local collections of nodes, locations, and JSON wrappers.

## Dependencies And Integration Points
Depends on `DatanodeDetails`, `HddsProtos.Node`, Jackson serializers, `JsonUtils`, SCM node query APIs, and service-loader registration as an `AdminSubcommand`.

## Risks And Test Signals
State validation is manual string comparison and error messages can reference the wrong variable. `node.getNodeOperationalStates(0)` and `getNodeStates(0)` assume at least one entry. Tests should cover filters, ordered/unordered output, full JSON port serialization, empty topology, and malformed states.
