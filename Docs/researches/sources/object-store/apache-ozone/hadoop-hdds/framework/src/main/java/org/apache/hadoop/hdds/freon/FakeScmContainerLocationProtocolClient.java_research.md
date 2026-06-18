# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/freon/FakeScmContainerLocationProtocolClient.java

## Purpose

This fake client returns SCM container-location protocol responses for Freon node queries. It is a lightweight stand-in for SCM when tests need healthy datanode metadata.

## Important APIs, Types, and Functions

`submitRequest(ScmContainerLocationRequest)` handles only `Type.QueryNode`. It builds a `NodeQueryResponseProto` from every fake datanode in `FakeClusterTopology.INSTANCE`.

## Control Flow

For `QueryNode`, it iterates over all fake datanodes, wraps each as an `HddsProtos.Node` with `NodeState.HEALTHY`, and returns a response with `Status.OK`. Unsupported commands throw, are caught, logged, and produce `null`.

## State and Persistence Behavior

There is no local mutable state or persistence; all topology comes from `FakeClusterTopology`.

## Dependencies and Integration Points

It depends on storage-container-location protobufs and the Freon fake topology singleton.

## Risks and Test Signals

All fake nodes are always healthy and localhost, so load tests cannot simulate stale/dead/maintenance states. `null` on unsupported requests can hide protocol misuse. Tests should verify every fake datanode appears once, the status is OK, and unsupported command handling is visible to callers.
