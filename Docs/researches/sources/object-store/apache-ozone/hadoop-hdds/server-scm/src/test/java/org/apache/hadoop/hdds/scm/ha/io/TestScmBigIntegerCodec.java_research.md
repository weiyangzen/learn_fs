# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmBigIntegerCodec.java

Purpose: minimal serialization round-trip test for `ScmBigIntegerCodec`, which is part of SCM HA request/response argument encoding.

Important APIs and types: the test constructs `ScmBigIntegerCodec`, serializes `BigInteger.valueOf(100)` to protobuf `ByteString`, deserializes it, and asserts equality with JUnit `assertEquals`.

Control flow: there is one JUnit method, `testCodec()`, with a straight-line encode/decode/assert path. No fixtures are required.

State and persistence: no persistent state is touched. The only state is the codec instance and local serialized bytes. Dependencies are `java.math.BigInteger` and Ratis-shaded protobuf `ByteString`.

Integration points: this test guards the codec used by SCM Ratis payloads when replicated methods carry `BigInteger` values. The signal is intentionally narrow; it does not test negative values, zero, very large values, null handling, or malformed bytes. Main risk is that codec behavior for edge-case `BigInteger` representations could regress without this test catching it.
