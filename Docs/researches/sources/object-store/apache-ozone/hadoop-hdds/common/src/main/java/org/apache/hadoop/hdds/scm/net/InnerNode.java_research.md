# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/InnerNode.java

## Purpose
Interface for non-leaf network topology nodes such as racks, datacenters, regions, or logical groups.

## Important APIs, Types, And Functions
Nested `Factory` constructs inner nodes. Main APIs add/remove nodes, find nodes by path, count/list nodes at relative levels, select leaves by index with excluded scopes/nodes and ancestor generation, and serialize to `HddsProtos.NetworkNode`.

## Control Flow
Implementations maintain a tree. SCM placement code adds datanodes, removes them, and chooses leaves while respecting topology exclusions.

## State And Persistence
The interface has no state; implementations hold topology tree state. Protobuf serialization supports transport/inspection.

## Dependencies And Integration Points
Extends `Node` and integrates with `NetworkTopology`, placement policies, and datanode topology protobufs.

## Risks And Test Signals
Relative level semantics and exclusion interactions are easy to implement incorrectly. Tests should cover add/remove, leaf indexing, excluded scopes, ancestor generation, equality, and protobuf output.
