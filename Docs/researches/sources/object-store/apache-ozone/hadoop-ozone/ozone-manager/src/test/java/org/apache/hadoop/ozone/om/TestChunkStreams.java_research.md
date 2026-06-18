<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestChunkStreams.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestChunkStreams.java

Purpose: Unit tests for `KeyInputStream` reading across multiple `BlockInputStream`s.

Important APIs/types/functions: Creates five anonymous `BlockInputStream` instances backed by 100-byte slices of a random 500-byte string. Tests use `KeyInputStream.read`, `getCurrentStreamIndex`, and `getRemainingOfIndex`.

Control flow: `testReadGroupInputStream` reads 500 bytes in one call and asserts the full string. `testErrorReadGroupInputStream` reads 340 bytes, checks stream index and remaining bytes in the fourth stream, then reads beyond EOF request size and verifies only remaining 160 bytes are returned, followed by `-1` EOF.

State and persistence behavior: No persistence. Anonymous streams track a local `pos` and byte-array input cursor.

Dependencies and integration points: Tests client-side read composition across block streams, using `OzoneClientConfig` with checksum verification enabled. The custom streams bypass real datanodes and checksums.

Risks: The anonymous `read(byte[],off,len)` increments `pos` by `readLen` even if EOF returned `-1`, though fixed 100-byte slices avoid that path in normal reads. Random ASCII content can include edge characters but is compared as UTF-8. Seek behavior is unsupported and untested.

Test signals: Passing confirms sequential multi-block reads, partial reads across block boundaries, current stream accounting, remaining-byte accounting, and EOF behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestChunkStreams.java -->
