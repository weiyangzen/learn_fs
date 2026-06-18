## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/checksum/ECBlockChecksumComputer.java

### Purpose
`ECBlockChecksumComputer` computes block checksums for erasure-coded blocks from stripe checksum metadata, excluding parity checksum bytes so the file checksum reflects only data bytes.

### Important APIs and Types
It stores chunk info list, `OmKeyInfo`, and block length. `compute` dispatches to `computeMd5Crc` or `computeCompositeCrc`. `getParityBytes` derives parity checksum byte count from `ECReplicationConfig.getParity()`, chunk length, and bytes per CRC.

### Control Flow
MD5 mode iterates chunk stripe checksums, verifies byte count alignment, limits each stripe checksum buffer to exclude parity bytes, and updates an MD5 digest. Composite CRC mode determines Hadoop checksum type from the first chunk, creates a `CrcComposer`, strips parity bytes, then feeds checksum ints with lengths bounded by bytes-per-CRC and remaining block length, with special handling for the last stripe's shorter chunk.

### State and Persistence Behavior
The object computes a local output byte buffer only. It reads EC replication configuration from `OmKeyInfo`.

### Dependencies and Integration Points
It depends on EC replication config, container `ChunkInfo` stripe checksums, Hadoop `DataChecksum`, `CrcComposer`, protobuf `ByteString`, and `MD5Hash`. It is created by `ECFileChecksumHelper`.

### Risks and Edge Cases
`computeMd5Crc` calls `digester.digest()` twice: once assigned to `fileMD5` and again in `setOutBytes`, so the stored output can become the digest of an already-reset digest rather than the intended digest. Parity byte calculation assumes four-byte CRC values and stripe checksum layout. Missing stripe checksums or unsupported checksum types fail at runtime. Composite CRC block length accounting is subtle for final partial stripes.

### Test Signals
Tests should include EC MD5 output correctness, composite CRC with partial final stripe, parity stripping for different data/parity layouts, null stripe checksum rejection, unsupported checksum types, and regression coverage for the double-digest behavior.
