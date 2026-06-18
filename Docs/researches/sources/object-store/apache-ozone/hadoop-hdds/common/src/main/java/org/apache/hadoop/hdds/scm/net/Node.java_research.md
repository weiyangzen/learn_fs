# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/Node.java

## Purpose
Base interface for any node in SCM network topology, whether an inner node or datanode leaf.

## Important APIs, Types, And Functions
Methods expose and mutate network location/name, full path, parent, ancestor, level, cost, leaf count, ancestor/descendant checks, and optional protobuf conversion via default `toProtobuf`.

## Control Flow
Topology implementations set parent/level/location as nodes are inserted. Placement code uses ancestor/descendant checks and cost/leaf counts.

## State And Persistence
Interface has no state. Implementations usually represent in-memory topology nodes and may serialize to HddsProtos.

## Dependencies And Integration Points
Depends on HddsProtos. Extended by `InnerNode` and implemented by `NodeImpl` and datanode detail classes.

## Risks And Test Signals
The default `toProtobuf` returns null, so callers must account for implementations that do not override it. Tests should cover path/name mutation and ancestor semantics in concrete classes.
