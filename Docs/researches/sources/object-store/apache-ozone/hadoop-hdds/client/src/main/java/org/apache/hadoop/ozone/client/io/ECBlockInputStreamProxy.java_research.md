# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStreamProxy.java

## Purpose
`ECBlockInputStreamProxy` is the top-level EC block-group reader. It chooses direct EC reading when enough data locations are available and fails over to reconstruction when locations are missing or direct reads fail.

## Important APIs and Types
Static helpers `expectedDataLocations` and `availableDataLocations` compute required and available data indexes. Public APIs include `read(byte[], int, int)`, `read(ByteBuffer)`, `seek`, `getPos`, `getRemaining`, `getLength`, `getBlockID`, `unbuffer`, and `close`.

## Control Flow
Construction calls `setReaderType()` to compare expected data locations against pipeline indexes, then `createBlockReader()`. Reads loop until the caller buffer fills or remaining bytes reach zero. If the active reader throws `BadDataLocationException` and it is not already a reconstruction reader, the proxy records failed locations, closes the direct reader, creates a reconstruction reader, seeks to the last position, resets the caller buffer to the mark, and retries. Seek failures in direct mode also trigger reconstruction failover.

## State and Persistence Behavior
State is the active `BlockExtendedInputStream`, reconstruction mode flag, failed location list, closed flag, and immutable construction dependencies. No persistence occurs.

## Dependencies and Integration Points
Created by `BlockInputStreamFactoryImpl` for EC replication configs. It depends on `ECBlockInputStreamFactory`, EC config, block location info, client factory, refresh callback, and client metrics for reconstruction totals/failures.

## Risks
Recursive retry after failover must preserve caller buffer marks and total read count. `failedLocations` is accumulated and passed into reconstruction; if it is incomplete, reconstruction may retry known-bad datanodes. Metrics are incremented only on reconstruction creation and reconstruction failure.

## Test Signals
`TestECBlockInputStreamProxy` covers expected/available location calculations, direct versus reconstruction reader creation, failover on bad locations, seek behavior, and close/unbuffer delegation.
