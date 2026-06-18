# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockOutputStreamEntry.java

Purpose: This `BlockOutputStreamEntry` subclass represents one erasure-coded block group. It fans a logical EC block group into one `ECBlockOutputStream` per data or parity replica and exposes cursor operations used by `ECKeyOutputStream` while writing stripes.

Important APIs and types: Important methods include `checkStream`, `getOutputStream`, `useNextBlockStream`, `forceToFirstParityBlock`, `resetToFirstEntry`, `markFailed`, `executePutBlock`, `streamsWithWriteFailure`, `streamsWithPutBlockFailure`, `calculateChecksum`, and `updateBlockGroupToAckedPosition`. It depends on `ECReplicationConfig`, single-node `Pipeline` construction, `ECBlockOutputStream`, protobuf chunk metadata, and async response futures.

Control flow: Lazy initialization creates an array of streams for all required EC nodes, each with a single-node pipeline carrying the original EC pipeline ID and replica index. The current stream cursor advances across data cells and parity cells. Data writes increment logical position; parity writes intentionally do not. After stripe writes, failures are detected from chunk or putBlock futures, checksums are concatenated from the latest chunk entries, putBlock is executed for every initialized stream, and close updates the block group ID from the first stream.

State and persistence behavior: Runtime state includes the stream array, current internal stream index, logical length, and last successful block-group ack length. Persistent effects are the data/parity chunks and putBlock metadata written by the underlying `ECBlockOutputStream`s. The class also updates block commit sequence information from the underlying stream.

Dependencies and integration points: It is created by `ECBlockOutputStreamEntryPool` and driven by `ECKeyOutputStream`. It integrates EC replication metadata, datanode replica indexes, xceiver client management, buffer pooling, tokens, metrics, and container protocol futures.

Risks: Failure detection treats null futures as failed; incomplete stream initialization can affect close and checksum behavior. `underlyingBlockID` assumes stream 0 exists when data has been written. The TODO around `getWrittenDataLength` notes retry accounting may be incomplete for parity or duplicate writes. Checksum concatenation relies on chunk-list alignment across data and parity streams.

Test signals: Strong tests cover single-node pipeline replica indexes, data-only position accounting, parity cursor transitions, flush/close over initialized streams only, write and putBlock future failure detection, failed server aggregation, checksum construction for partial stripes, and ack length updates after successful putBlock.
