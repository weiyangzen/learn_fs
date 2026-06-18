# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueContainerCheck.java

## Purpose
`KeyValueContainerCheck` implements integrity scans for key-value containers. `fastCheck` verifies container metadata structure and descriptor consistency. `fullCheck` is a superset for closed/quasi-closed/unhealthy containers that walks block metadata, verifies chunk files and checksums, and builds a Merkle tree of observed data.

## Important APIs and Types
The constructor receives `ConfigurationSource` and a live `KeyValueContainer`. Public APIs are `fastCheck()` returning `MetadataScanResult` and `fullCheck(DataTransferThrottler, Canceler)` returning `DataScanResult`. Key helpers include `scanMetadata`, `checkContainerFile`, `scanData`, `scanBlock`, `verifyChecksum`, `blockInDBWithLock`, and `loadContainerData`.

## Control Flow
`fastCheck` runs `scanMetadata`, converts collected `ContainerScanError`s into a result, and reports deleted if in-memory state became DELETED. Metadata scanning checks the container directory, metadata directory, `.container` file existence/readability, descriptor checksum/type/id/db type/metadata path, and chunks directory presence. `fullCheck` first runs `fastCheck`; if metadata is healthy it opens the DB, iterates block entries with the container's schema-aware unprefixed key filter, and scans each block unless deletion is detected. Chunk scanning locates layout-specific chunk files, handles EC empty padding blocks, verifies per-checksum bytes using `Checksum`, throttles reads, records observed checksums into a `ContainerMerkleTreeWriter`, and suppresses errors if a missing file corresponds to a block concurrently deleted from DB under container read lock.

## State and Persistence
The checker does not modify persistent state. It loads a separate `KeyValueContainerData` instance from disk and uses live in-memory container data to detect deletion during scans. It reads DB files and chunk files, uses a static `DirectBufferPool`, and builds scan result objects containing errors and a Merkle tree.

## Dependencies and Integration Points
`KeyValueContainer.scanMetaData` and `scanData` instantiate this class. Background and on-demand scanner services consume the results. It depends on container YAML utilities, block DB helpers, layout-version chunk lookup, checksum utilities, direct buffer pooling, scanner result/error types, and HDFS throttling/cancelation classes.

## Risks and Test Signals
The scanner intentionally runs much of the data scan without holding the container lock, so it must distinguish real corruption from concurrent block deletion. Buffer return is manual; checksum verification paths should not leak direct buffers on unexpected runtime errors. Missing chunks with zero-length EC padding are not treated as corruption. Tests in `TestKeyValueContainerCheck` cover no-corruption, corrupt metadata, corrupt chunks, checksum output, deleted containers, and scan result behavior across schema/layout variants. Scanner integration tests cover background and on-demand invocation.
