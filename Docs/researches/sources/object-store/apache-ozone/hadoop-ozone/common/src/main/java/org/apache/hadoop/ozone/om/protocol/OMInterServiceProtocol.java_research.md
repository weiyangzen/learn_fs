<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMInterServiceProtocol.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMInterServiceProtocol.java

## Purpose

`OMInterServiceProtocol` defines RPCs used between OM services, currently for bootstrapping a new OM node.

## Important APIs, Types, And Functions

It extends `Closeable` and declares `bootstrap(OMNodeDetails newOMNode)`.

## Control Flow, State, And Persistence

The interface has no implementation. Server implementations handle bootstrap flow, likely transferring metadata or configuration required to join the OM HA ring. State changes occur in OM storage and Ratis/HA configuration layers.

## Dependencies And Integration Points

It depends on `OMNodeDetails` and IO close/exception types. It integrates with OM HA add-node workflows and inter-service protocol translators.

## Risks And Test Signals

Bootstrap is sensitive to node identity and cluster membership. Tests should cover valid new node details, duplicate node IDs, network failures, idempotent retries, and client translator close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMInterServiceProtocol.java -->
