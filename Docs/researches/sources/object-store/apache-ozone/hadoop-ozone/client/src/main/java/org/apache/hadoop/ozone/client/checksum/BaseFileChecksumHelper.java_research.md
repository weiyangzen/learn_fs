## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/BaseFileChecksumHelper.java

### Purpose
`BaseFileChecksumHelper` orchestrates Ozone file checksum computation across key blocks. It fetches block locations, retrieves chunk checksum data through subclass hooks, computes per-block checksums, combines them into Hadoop-compatible file checksum results, and reuses cached OM checksums when possible.

### Important APIs and Types
Important fields include `OmKeyInfo`, `OzoneVolume`, `OzoneBucket`, key name, requested length, `ClientProtocol`, combine mode, checksum type, `DataOutputBuffer` for block checksums, `XceiverClientFactory`, `FileChecksum`, key location list, remaining requested bytes, bytes per CRC, and CRCs per block. Abstract hooks are `getBlockChecksumComputer` and `getChunkInfos`. Public `compute` and `getFileChecksum` drive the lifecycle.

### Control Flow
Construction stores context, obtains `XceiverClientFactory` by casting `ClientProtocol` to `RpcClient`, and fetches blocks when length is positive. `fetchBlocks` looks up latest key locations if no `OmKeyInfo` was provided, reuses `keyInfo.getFileChecksum()` for full-length reads, and stores latest-version block locations. `compute` returns cached checksum if available, returns the Hadoop empty-file MD5/CRC checksum for no blocks, otherwise calls `checksumBlocks` and creates the final result. `checksumBlock` gets chunk infos, determines checksum type and bytes-per-checksum from the first chunk, truncates by requested remaining length, delegates block checksum computation, and appends raw block checksum bytes according to the combine mode.

`makeFinalResult` supports `MD5MD5CRC` and `COMPOSITE_CRC`. MD5 mode digests the per-block MD5s and returns gzip or Castagnoli Hadoop checksum based on checksum type. Composite CRC mode composes block CRCs using `CrcComposer` and returns `CompositeCrcFileChecksum`.

### State and Persistence Behavior
The helper is stateful for one compute operation: remaining length decreases as blocks are processed, checksum buffer accumulates, and `fileChecksum` is set once. It does not persist server state. It reads OM metadata and DataNode block metadata.

### Dependencies and Integration Points
It integrates with OM lookup (`OzoneManagerProtocol.lookupKey`), DataNode checksum retrieval via subclasses, Hadoop `FileChecksum` classes, `MD5Hash`, `DataChecksum`, `CrcComposer`, `CrcUtil`, and `ChecksumHelperFactory`.

### Risks and Edge Cases
The direct cast to `RpcClient` means non-RPC `ClientProtocol` implementations are unsupported for checksum computation. `crcPerBlock` is never updated in this class, so MD5MD5CRC results may rely on legacy assumptions or subclass side effects that are not present here. The loop condition `remaining >= 0` allows processing when remaining is zero before early length checks stop future work. Composite CRC assumes four bytes per block checksum in the buffer. Cached OM checksum is reused only for full-length reads.

### Test Signals
Tests should cover cached full-length checksum reuse, zero-length/empty-key checksum result, partial length computation, MD5MD5CRC for CRC32 and CRC32C, composite CRC composition across multiple blocks, failure on empty chunk infos, unsupported checksum/combine modes, and behavior with mocked/non-RPC `ClientProtocol`.
