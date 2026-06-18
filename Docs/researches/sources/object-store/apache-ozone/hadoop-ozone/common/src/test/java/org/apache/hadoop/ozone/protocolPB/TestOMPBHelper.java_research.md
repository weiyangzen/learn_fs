# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/protocolPB/TestOMPBHelper.java

Purpose: regression test for `OMPBHelper.convertMD5MD5FileChecksum`, ensuring backward compatibility with a prior 20-byte MD5 protobuf bug.

Important APIs/types/functions: exercises `OMPBHelper.convertMD5MD5FileChecksum`, protobuf `MD5MD5Crc32FileChecksumProto`, `ChecksumTypeProto`, Hadoop `MD5MD5CRC32FileChecksum`, and `MD5Hash.MD5_LEN`.

Control flow and state: runs the same conversion with a normal 16-byte MD5 and a buggy 20-byte buffer whose final four bytes are zero. It writes the resulting checksum to a byte stream, reads bytes-per-CRC, CRC-per-block, and MD5 bytes back from a `ByteBuffer`, and asserts only the first 16 bytes are retained.

Dependencies and integration points: uses `ByteString`, Hadoop checksum classes, random values, and `StringUtils.bytes2Hex` for diagnostic output. This helper affects protocol compatibility for file checksum responses.

Risks and test signals: catches checksum conversion failures for historical persisted/wire data. Randomized bytes-per-CRC and crc-per-block increase coverage, but the test uses random diagnostics and prints to stdout.
