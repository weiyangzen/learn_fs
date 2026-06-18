# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/Buffers.java

## Purpose
`Buffers` is a package-private streaming helper that retains the last `max` bytes of reference-counted buffers while exposing older buffers as safe to flush.

## Important APIs, Types, And Functions
It stores a deque of `ReferenceCountedObject<ByteBuffer>`, `max`, and `length`. Methods are `offer`, `poll`, `pollAll`, and `cleanUpAll`; private helpers decide whether head buffers are extra.

## Control Flow
`offer` retains and queues a buffer, then returns an iterator that polls head buffers while at least `max` bytes remain. `pollAll` drains retained buffers into a read-only Netty `ByteBuf` wrapper whose release callback releases the wrapped buffer and all source references. `cleanUpAll` releases queued references.

## State And Persistence
All state is in-memory buffer ownership. It does not persist data directly, but it affects streaming write durability indirectly by deciding which buffers may be written and which are retained for put-block metadata.

## Dependencies And Integration Points
It depends on Guava preconditions, Ratis reference-counted objects/helper logging, Netty `ByteBuf`, and `KeyValueStreamDataChannel`. It is used by streaming file-per-block writes.

## Risks And Test Signals
Risks include reference-count leaks, premature release, retaining too much or too little data, and invariant failures around exact `max` boundaries. Tests should cover variable buffer sizes, exact-retention cases, `pollAll` release behavior, and cleanup after exceptions.
