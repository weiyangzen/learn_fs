# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestBucket.java

## Purpose
`TestBucket` is a test wrapper around `OzoneBucket` that simplifies creating buckets, writing keys with deterministic or random data, opening key input streams, and validating read buffers against written data.

## Important APIs, Types, and Functions
- `newBuilder(OzoneClient)` returns a builder that creates a volume and bucket if names are not supplied.
- `delegate()` exposes the wrapped `OzoneBucket`.
- `getKeyInputStream(...)` unwraps `readKey(...).getInputStream()` as `KeyInputStream`.
- `writeKey(...)` overloads write fixed-length string data or supplied bytes with `RatisReplicationConfig` defaulting to factor three.
- `writeRandomBytes(...)` writes random bytes through the same path.
- `validateData(...)` compares a read window to the expected slice of original input.

## Control Flow
The builder obtains the object store, creates a random volume if needed, creates a random bucket if needed, and wraps the resulting bucket. Write helpers generate data, delegate to `TestDataUtil.createKey`, and return the bytes for later validation.

## State and Persistence Behavior
The helper creates real Ozone volume, bucket, and key metadata/data. The wrapper itself holds only an `OzoneBucket` reference and does not manage cleanup.

## Dependencies and Integration Points
Dependencies include Ozone client/object-store APIs, `TestDataUtil`, `ContainerTestHelper`, Ratis replication config, `KeyInputStream`, and `ThreadLocalRandom`.

## Risks and Test Signals
Risks include implicit random names complicating diagnosis and default replication factor three requiring enough datanodes. Signals are successful key creation and byte-for-byte validation through `assertArrayEquals`.
