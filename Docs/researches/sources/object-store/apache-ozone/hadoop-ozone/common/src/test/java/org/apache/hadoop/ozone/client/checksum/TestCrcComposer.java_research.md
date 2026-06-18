# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/client/checksum/TestCrcComposer.java

Purpose: tests `CrcComposer` composition of per-chunk CRCs into either a single unstriped CRC or striped cell CRCs.

Important APIs/types/functions: uses `CrcComposer.newCrcComposer`, `newStripedCrcComposer`, `update(byte[], ...)`, `update(DataInputStream, ...)`, `update(int, ...)`, `digest`, and `CrcUtil.readInt/writeInt`. It uses Hadoop `DataChecksum.Type.CRC32C`.

Control flow and state: setup creates deterministic random data, full-data CRC, eight chunk CRCs of size 10 with a partial final chunk, and four cell CRCs of size 20 with a partial final cell. Tests feed CRCs through byte arrays, streams, and single-int updates. Striped tests verify chunk CRCs aggregate to expected cell CRC byte arrays.

Dependencies and integration points: integrates with Hadoop checksum math and Ozone client checksum storage formats. Multi-stage tests compose chunk CRCs into cells, then compose cells into the full object CRC.

Risks and test signals: detects incorrect final-part length handling, stripe boundary crossings, and byte-array CRC-length misalignment. The incorrect-chunk-size test proves callers must pass the real covered data length for the final CRC.
