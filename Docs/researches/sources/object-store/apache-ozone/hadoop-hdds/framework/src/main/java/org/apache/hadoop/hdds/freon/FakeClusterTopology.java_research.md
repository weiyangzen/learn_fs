# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/freon/FakeClusterTopology.java

## Purpose

`FakeClusterTopology` pre-generates deterministic-shape but random-identity datanodes and RATIS pipelines for Freon load tests. It gives fake SCM protocol clients enough topology to allocate blocks and query nodes without contacting a real SCM.

## Important APIs, Types, and Functions

`INSTANCE` is a static singleton with nine datanodes and three pipelines. `getRandomPipeline()` returns one pipeline selected by `Random`; `getAllDatanodes()` returns the unmodifiable datanode list. `createDatanode()` builds localhost protobuf datanodes with a RATIS port.

## Control Flow

Static initialization loops over nine nodes, creates a datanode each iteration, and after every third node builds a RATIS/THREE pipeline containing the last three nodes. Exceptions are logged and the topology is still wrapped.

## State and Persistence Behavior

State is in-memory only: unmodifiable lists of `DatanodeDetailsProto` and `Pipeline`, plus a non-secure `Random`.

## Dependencies and Integration Points

It depends on HDDS protobuf types and `PipelineID.randomId()`. `FakeScmBlockLocationProtocolClient` and `FakeScmContainerLocationProtocolClient` use the singleton.

## Risks and Test Signals

The fake topology assumes exactly three-node RATIS pipelines and localhost endpoints, so it is not suitable for production-like network behavior. If initialization failed before pipeline creation, `getRandomPipeline()` could fail on an empty list. Tests should validate nine datanodes, three pipelines, immutable lists, and stable protobuf shape.
