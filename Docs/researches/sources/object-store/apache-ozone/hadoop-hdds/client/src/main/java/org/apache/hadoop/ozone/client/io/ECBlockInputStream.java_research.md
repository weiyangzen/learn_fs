# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStream.java

## Purpose
`ECBlockInputStream` reads an EC block group directly when all required data locations are available. It maps logical block-group offsets to internal EC data block streams and reads one EC cell at a time.

## Important APIs and Types
Important APIs are `read(byte[], int, int)`, `read(ByteBuffer)`, `readWithStrategy`, `seek`, `getPos`, `getLength`, `getBlockID`, `hasSufficientLocations`, `currentStreamIndex`, `getOrOpenStream`, `internalBlockLength`, and `ecPipelineRefreshFunction`. It stores EC config, chunk/stripe size, block location info, data locations, spare locations, per-index internal streams, failed locations, position, and seek flag.

## Control Flow
The constructor extracts EC replica indexes from the block pipeline into `dataLocations` and spare lists. Reads use `currentStreamIndex()` to pick the data replica for the current logical EC cell, lazily open a standalone one-node block stream for that replica, bound the read by EC chunk boundary, caller buffer, and block remaining bytes, then advance logical position. If a direct stream fails, `BadDataLocationException` triggers replacement with a spare location and retry; otherwise the exception propagates to the proxy for reconstruction failover.

## State and Persistence Behavior
State is in-memory reader position, per-index stream cache, location arrays, failed location list, and seek flag. It reads persisted internal block data through standalone pipelines and does not persist data.

## Dependencies and Integration Points
Created by `ECBlockInputStreamFactoryImpl` for non-reconstruction EC reads. It uses `BlockInputStreamFactory` to create internal standalone block streams, `ECReplicationConfig`, `Pipeline` replica indexes, `StandaloneReplicationConfig`, and `BadDataLocationException`.

## Risks
Correct EC offset math is central: `internalBlockLength`, `currentStreamIndex`, and lazy `seekStreamIfNecessary` must align with EC chunk and stripe sizes. Spare location handling only retries if a spare exists for the same index; otherwise proxy-level reconstruction is needed. The direct reader assumes data locations are sufficient for the block length.

## Test Signals
`TestECBlockInputStream` covers internal block length, direct reads, seek behavior, spare datanode retry, and failure cases. `TestECBlockInputStreamProxy` covers proxy failover from this reader.
