# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/SeekableIterator.java

## Purpose

`SeekableIterator<K, E>` extends `ClosableIterator<E>` with explicit repositioning support.

## APIs and control flow

The single added method is `seek(K position) throws IOException`, allowing an implementation to move to a key or logical position before continuing iteration.

## State, dependencies, and integration

The interface has no state and depends on Java `IOException` plus the local `ClosableIterator`. It integrates with DB/table scanners that can seek to a key prefix or resume point.

## Risks and test signals

The semantics of inclusive/exclusive seek are not defined by the interface and must be specified by implementations. Tests should cover implementation-specific seek positioning, seeking before/after bounds, resource closure, and iteration after seek.
