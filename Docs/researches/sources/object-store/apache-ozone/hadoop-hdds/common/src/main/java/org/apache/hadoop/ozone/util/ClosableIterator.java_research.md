# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/ClosableIterator.java

## Purpose

`ClosableIterator<E>` marks iterators that hold resources and must be closed after use.

## APIs and control flow

The interface extends `Iterator<E>` and `Closeable`, narrowing `close()` to a no-throws method. It does not define automatic close behavior on exhaustion.

## State, dependencies, and integration

The interface has no state and depends only on Java `Iterator` and `Closeable`. It integrates with metadata table scanners, DB iterators, and any Ozone iterator wrapper around native or IO-backed resources.

## Risks and test signals

Callers must use try/finally or try-with-resources even though `close()` has no checked exception. Tests belong on implementations and should check resource release on early exit, exhaustion, and repeated close.
