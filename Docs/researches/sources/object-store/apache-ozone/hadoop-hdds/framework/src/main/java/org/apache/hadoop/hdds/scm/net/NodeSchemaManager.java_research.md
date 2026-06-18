# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/NodeSchemaManager.java

## Purpose
`NodeSchemaManager` is the runtime holder for network topology schema metadata. It initializes schemas from configuration or tests, stores them from root to leaf, exposes level costs, completes partial paths when prefix enforcement is enabled, and converts protobuf network nodes back into in-memory topology nodes.

## Important APIs, Types, And Functions
`init(ConfigurationSource)` reads `OZONE_SCM_NETWORK_TOPOLOGY_SCHEMA_FILE`; `init(String)` directly loads a file; test-only `init(NodeSchema[], boolean)` injects schemas. `getMaxLevel()` and `getCost(int)` expose topology metadata. `complete(String)` fills missing inner levels using schema default names. `fromProtobuf(HddsProtos.NetworkNode)` dispatches to `DatanodeDetails` or `InnerNodeImpl`.

## Control Flow
Initialization delegates to `NodeSchemaLoader`, copies the returned schema list, records `enforcePrefix`, and sets `maxLevel` to the number of schema layers. `complete()` normalizes the input path, returns `null` when prefixes are not enforced, returns the original path when already complete, otherwise scans input components against inner-node schema prefixes and inserts defaults for missing levels before appending the leaf component.

## State, Persistence, And Dependencies
State is held in process fields: `allSchema`, `enforcePrefix`, and `maxLevel`. There is no persistence beyond the loaded schema file. Dependencies include SCM config keys, topology utilities, Guava `Preconditions`, protobuf models, and datanode/topology conversion classes.

## Integration Points
The manager is the shared schema authority for SCM topology-aware placement and RPC reporting. `ScmBlockLocationProtocolClientSideTranslatorPB` reconstructs network topology trees from protobufs that use the same `Node` model.

## Risks
Singleton creation is not synchronized. Methods assume `init()` has been called; otherwise `allSchema` and `maxLevel` can be invalid. `complete()` uses string splitting on normalized paths and returns `null` on ambiguous paths, so callers need a fallback. The method returns the original `path` when complete rather than the normalized path.

## Test Signals
Tests should exercise config-based loading, injected schemas, prefix and non-prefix completion, invalid level cost requests, protobuf conversion for datanodes and inner nodes, and behavior before initialization.
