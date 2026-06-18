# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/client/checksum/TestCrcUtil.java

Purpose: validates low-level CRC utility serialization, formatting, and Galois-field multiplication used by Ozone checksum composition.

Important APIs/types/functions: covers `CrcUtil.intToBytes`, `writeInt`, `readInt`, `toSingleCrcString`, `toMultiCrcString`, and `multiplyMod`. It also exposes shared helper `assertContains` for checksum tests and contains a nested benchmark driver.

Control flow and state: tests assert big-endian integer serialization and string formatting for zero, one, and multiple CRC values. `testMultiplyMod` generates 10 million random pairs for CRC32 and CRC32C, computes expected values via a reference `galoisFieldMultiply`, and compares optimized table multiplication.

Dependencies and integration points: uses Hadoop `DataChecksum.Type` and Hadoop `org.apache.hadoop.util.CrcUtil` polynomials/constants. The multiplication routine underpins `CrcComposer` and therefore checksum verification across chunk and stripe boundaries.

Risks and test signals: protects against endian changes, malformed CRC byte-array length acceptance, and arithmetic regressions in CRC polynomial multiplication. The random large-loop test is strong but can be expensive and timing-sensitive; timeout is set to 10 seconds for the test class.
