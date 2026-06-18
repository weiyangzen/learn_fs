# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeReportHandler.java

Purpose: tests `NodeReportHandler` updates SCM node capacity metrics from datanode node reports.

Important APIs and types: setup creates `SCMNodeManager` with mocked `SCMStorageConfig`, `HDDSLayoutVersionManager`, `NetworkTopologyImpl`, event queue, and empty SCM context. The test class implements `EventPublisher`, logging published events. `getNodeReport()` wraps generated protobuf `NodeReportProto` in `NodeReportFromDatanode`.

Control flow: `testNodeReport()` creates storage and metadata reports for a random datanode, confirms no node metric exists before registration, registers the node with one storage report, checks capacity/remaining/scmUsed values, then invokes `nodeReportHandler.onMessage()` with two storage reports and verifies aggregated metrics double.

State and persistence: temp directories provide storage path strings, but no disk data is persisted. Node manager state holds reports and derived `SCMNodeMetric`.

Integration points and risks: protects heartbeat report ingestion and metric aggregation. It does not validate emitted events beyond logging, nor does it cover failed reports, missing metadata reports, filesystem fields, or multi-datanode aggregation.
