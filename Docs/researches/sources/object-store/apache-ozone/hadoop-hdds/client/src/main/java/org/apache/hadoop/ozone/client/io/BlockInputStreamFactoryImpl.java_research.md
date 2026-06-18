# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockInputStreamFactoryImpl.java

## Purpose
`BlockInputStreamFactoryImpl` chooses the concrete block reader for a block: EC proxy reader for EC replication, streaming block reader when enabled and supported by all datanodes, or classic `BlockInputStream` otherwise.

## Important APIs and Types
Static `getInstance(ByteBufferPool, Supplier<ExecutorService>)` creates the factory with EC reconstruction dependencies. Constructors wire `ECBlockInputStreamFactoryImpl`. `create(...)` selects the stream. `createBlockInputStream(...)` explicitly creates a classic Ratis/standalone `BlockInputStream`.

## Control Flow
`create` checks `repConfig.getReplicationType()`. EC configs produce `ECBlockInputStreamProxy`. Non-EC configs check `config.isStreamReadBlock()` and all pipeline datanode versions against `STREAM_BLOCK_SUPPORT`; if true, it creates `StreamBlockInputStream`, otherwise `BlockInputStream`.

## State and Persistence Behavior
State is the EC helper factory. It does not persist data.

## Dependencies and Integration Points
It integrates Ozone client IO with `BlockInputStream`, `StreamBlockInputStream`, `ECBlockInputStreamProxy`, `ECBlockInputStreamFactoryImpl`, `ElasticByteBufferPool`, and datanode version gates.

## Risks
Feature selection is version-sensitive. A single older datanode disables streaming reads for the whole pipeline. EC creation delegates to a proxy that may create further internal streams; incorrect replication config passed to internal creation could cause recursion or wrong stream type.

## Test Signals
`TestBlockInputStreamFactoryImpl` validates stream selection for EC, stream-read support, and fallback behavior.
