# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/InnerNodeImpl.java

## Purpose

`InnerNodeImpl` is the mutable tree-node implementation for Ozone network topology. Inner nodes represent topology scopes such as datacenters or racks; leaves are datanodes.

## Important APIs, Types, and Functions

It implements `InnerNode` with child management, leaf counts, path lookup, level queries, indexed leaf selection, exclusion-aware leaf selection, protobuf serialization/deserialization, equality, and a `Factory`. Children are kept in insertion order in a `LinkedHashMap` keyed by network name.

## Control Flow

`add(Node)` validates ancestry, creates missing intermediate inner nodes, attaches leaves, and increments `numOfLeaves` along the path only for new additions. `remove(Node)` recursively removes leaves, prunes empty inner nodes, and decrements counts. `getNode` handles absolute and relative paths. `getLeaf` walks children by accumulated leaf counts, with exclusion-aware variants subtracting excluded scopes and ancestor-derived counts.

## State and Persistence Behavior

State is the child map and descendant leaf count. `toProtobuf` persists node topology, leaves, and children; `fromProtobuf` reconstructs a tree, though parent links from deserialization depend on nested conversion behavior.

## Dependencies and Integration Points

It extends `NodeImpl`, uses `NodeSchemaManager` for costs and protobuf conversion, and is the default factory used by `NetworkTopologyImpl`.

## Risks and Test Signals

The class is described as thread-safe but does not lock internally; callers rely on `NetworkTopologyImpl` locks. Deserialized parent pointers may require validation. Tests should cover add/update/remove count invariants, path lookup, exclusion-aware selection, protobuf round trip, insertion-order leaf indexing, and equality.
