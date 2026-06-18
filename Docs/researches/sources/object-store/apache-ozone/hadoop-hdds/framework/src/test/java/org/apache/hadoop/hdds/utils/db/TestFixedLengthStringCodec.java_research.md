<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestFixedLengthStringCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestFixedLengthStringCodec.java

Purpose: tests that `FixedLengthStringCodec` can encode bytes into a string form and decode back to the original bytes for numeric container IDs.

Important APIs/types/functions: `FixedLengthStringCodec.bytes2String`, `FixedLengthStringCodec.string2Bytes`, `LongCodec.toByteArray`, and `LongCodec.fromByteArray`.

Control flow: iterates a range of long container IDs, converts each long to bytes, turns bytes into a fixed-length string, converts the string back to bytes, decodes the long, and asserts equality.

State and persistence behavior: pure in-memory byte/string conversion with no external state.

Dependencies and integration points: validates fixed-length string encoding used when binary keys need string-safe representation while preserving byte length/order assumptions.

Risks: coverage is focused on long byte arrays; multibyte string rejection and broader codec behavior are covered in `TestCodec`.

Test signals: asserts decoded container ID equals original for each generated ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestFixedLengthStringCodec.java -->
