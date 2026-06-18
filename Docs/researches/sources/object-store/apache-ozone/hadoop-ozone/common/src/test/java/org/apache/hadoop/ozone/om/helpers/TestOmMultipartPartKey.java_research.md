# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartPartKey.java

Purpose: validates byte-level codec behavior for `OmMultipartPartKey`, including prefix keys, full keys, upload IDs with slashes, sort order, and malformed input rejection.

Important APIs/types/functions: uses `OmMultipartPartKey.getCodec`, `of`, `prefix`, `hasPartNumber`, `getPartNumber`, `getUploadId`, `toString`, `Codec.toPersistedFormat`, `fromPersistedFormat`, `supportCodecBuffer`, `toHeapCodecBuffer`, and `fromCodecBuffer`.

Control flow and state: full keys encode upload ID plus a separator and big-endian int part number; prefix keys encode upload ID only. Parameterized tests cover all valid part numbers in `[1,10000]` whose low byte equals separator byte `0x2f`, ensuring the decoder finds the real separator. Byte comparison proves numerical part order sorts correctly.

Dependencies and integration points: integrates with HDDS `Codec`, `CodecBuffer`, and `CodecException`. The codec defines RocksDB key layout for multipart part entries.

Risks and test signals: catches naive slash splitting, malformed UTF-8 acceptance, empty/invalid key acceptance, null factory inputs, lexicographic part ordering bugs, and malformed surrogate encoding. This is high-risk persistence code because byte order controls DB scans.
