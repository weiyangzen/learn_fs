# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockInputStreamFactory.java

## Purpose
`BlockInputStreamFactory` abstracts creation of the correct block input stream implementation for a replication configuration.

## Important APIs and Types
It declares `create(ReplicationConfig, BlockLocationInfo, Pipeline, Token<OzoneBlockTokenIdentifier>, XceiverClientFactory, Function<BlockID, BlockLocationInfo>, OzoneClientConfig)`, returning `BlockExtendedInputStream`.

## Control Flow
Implementations decide among EC proxy readers, streaming block readers, and classic chunk-based block readers.

## State and Persistence Behavior
The interface has no state. Implementations may own helper factories and pools.

## Dependencies and Integration Points
Used by key input stream construction and EC readers that need to open standalone internal block streams. `BlockInputStreamFactoryImpl` is the primary implementation.

## Risks
The factory is part of recursive EC construction: EC direct/reconstruction readers use it to create internal standalone block streams. Implementations must avoid recursively creating EC readers for those standalone internal reads.

## Test Signals
`TestBlockInputStreamFactoryImpl`, `TestECBlockInputStream`, and EC stream utility factories validate factory decisions.
