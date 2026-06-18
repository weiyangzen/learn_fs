# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmBigIntegerCodec.java

Purpose: SCM HA request/response codec for `BigInteger` values, mainly certificate serial numbers.

Important APIs and types: Implements `ScmCodec<BigInteger>` with `serialize` and `deserialize`.

Control flow: Serialization wraps `BigInteger.toByteArray()` in a Ratis shaded `ByteString`. Deserialization creates a new `BigInteger` from the received byte array.

State and persistence behavior: Stateless. The encoded bytes travel in Ratis request/response messages, not directly in RocksDB.

Dependencies and integration points: Registered in `ScmCodecFactory` for certificate-store invocations and any HA method using `BigInteger`.

Risks and test signals: `BigInteger.toByteArray` is signed two's-complement, so byte compatibility depends on Java's standard form. Tests should cover positive, zero, large, and sign-bit-boundary values.
