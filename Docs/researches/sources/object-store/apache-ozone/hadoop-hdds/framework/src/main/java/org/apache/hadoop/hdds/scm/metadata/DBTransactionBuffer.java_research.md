# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/metadata/DBTransactionBuffer.java

## Purpose

`DBTransactionBuffer` abstracts SCM metadata writes so callers can add/remove table mutations without depending on whether updates are immediately applied or buffered for HA replication.

## Important APIs, Types, and Functions

It declares generic `addToBuffer(Table<KEY, VALUE>, KEY, VALUE)`, `removeFromBuffer(Table<KEY, VALUE>, KEY)`, and `close()`.

## Control Flow

Implementations decide whether calls write directly to tables or stage into a batch/Ratis transaction.

## State and Persistence Behavior

The interface has no state. Implementations may buffer persistent RocksDB mutations.

## Dependencies and Integration Points

It depends on HDDS DB `Table`, `CodecException`, and `RocksDatabaseException`. `SCMDBTransactionBufferImpl` is the non-Ratis direct implementation.

## Risks and Test Signals

Callers must close buffers when implementations require flushing/releasing resources. Tests should verify add/remove semantics through direct and HA implementations and exception propagation.
