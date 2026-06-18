# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStreamFactoryImpl.java

## Purpose
`ECBlockInputStreamFactoryImpl` constructs either direct EC readers or reconstruction readers, wiring the required byte-buffer pool and reconstruction executor.

## Important APIs and Types
Static `getInstance` creates the factory. The constructor stores a base `BlockInputStreamFactory`, `ByteBufferPool`, and `Supplier<ExecutorService>`. `create(...)` returns `ECBlockInputStream` or `ECBlockReconstructedInputStream`.

## Control Flow
If `missingLocations` is true, it creates an `ECBlockReconstructedStripeInputStream`, adds known failed datanodes, then wraps it in `ECBlockReconstructedInputStream` to provide normal stream semantics. Otherwise it creates direct `ECBlockInputStream`.

## State and Persistence Behavior
Factory state consists of dependencies only. It does not persist data.

## Dependencies and Integration Points
Used by `BlockInputStreamFactoryImpl` and `ECBlockInputStreamProxy`. It integrates `ByteBufferPool`, reconstruction executor supplier, direct EC reader, stripe reconstruction reader, and normal reconstructed stream wrapper.

## Risks
Each reconstruction reader obtains an executor from the supplier; lifecycle ownership is not handled in this factory, so supplier behavior matters. Passing failed locations before initialization is required because the stripe reader rejects failed-datanode updates after reads begin.

## Test Signals
Covered by `TestECBlockInputStreamProxy`, `TestECBlockInputStream`, and reconstructed EC tests that use factory paths and test factories.
