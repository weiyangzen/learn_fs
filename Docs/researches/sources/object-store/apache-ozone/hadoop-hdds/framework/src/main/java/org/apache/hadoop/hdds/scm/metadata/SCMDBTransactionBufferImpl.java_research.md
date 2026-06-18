# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMDBTransactionBufferImpl.java

## Purpose

`SCMDBTransactionBufferImpl` is the simple non-Ratis `DBTransactionBuffer` implementation for SCM metadata.

## Important APIs, Types, and Functions

`addToBuffer` calls `table.put`; `removeFromBuffer` calls `table.delete`; `close` is a no-op.

## Control Flow

Mutations are applied immediately to the supplied table rather than staged.

## State and Persistence Behavior

The object has no internal state. Persistence behavior is whatever the table implementation provides for `put` and `delete`.

## Dependencies and Integration Points

Used when SCM is not buffering mutations for Ratis. Depends on HDDS DB `Table`.

## Risks and Test Signals

The name says buffer, but this implementation writes immediately, so callers relying on atomic multi-table batching need a different implementation. Tests should verify immediate writes/deletes and no-op close.
