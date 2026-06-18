# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NodeImpl.java

## Purpose
Concrete leaf implementation of `Node` for network topology. It stores name, location, full path, level, parent, and traffic cost, and implements path/ancestor/descendant behavior.

## Important APIs, Types, And Functions
Constructors accept string or `StringWithByteString` name/location with optional parent/level. Getters/setters update cached full path. `getAncestor`, `isAncestor`, `isDescendant`, static `toProtobuf`, `equals`, `hashCode`, and `toString` are key.

## Control Flow
Construction validates names do not contain `/` and normalizes string locations. Mutating name/location recomputes path. Ancestor traversal follows parent links; path checks use case-insensitive equality and slash-suffixed prefix comparisons.

## State And Persistence
State is mutable in memory except final cost. No direct persistence; protobuf helper can serialize basic topology fields.

## Dependencies And Integration Points
Depends on Guava preconditions, HddsProtos, `StringWithByteString`, and `NetUtils`. Used by topology trees and placement code.

## Risks And Test Signals
Comments claim thread safety but mutable fields are unsynchronized. `getPath` can include `StringWithByteString.toString()` for non-root name concatenation. Tests should cover normalization, equality, root behavior, path mutation, ancestor/descendant edge cases, and protobuf helper output.
