# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmStringCodec.java

Purpose: SCM HA codec for UTF-8 `String` values.

Important APIs and types: Public `ScmCodec<String>` implementation using `StandardCharsets.UTF_8`.

Control flow: Serialization converts the string to UTF-8 bytes and wraps them in shaded `ByteString`; deserialization builds a new Java string from the byte array using UTF-8.

State and persistence behavior: Stateless and used for Ratis messages.

Dependencies and integration points: Registered in `ScmCodecFactory`; used by sequence id names, service names, root CA rotation ids, and other string parameters.

Risks and test signals: No null handling is provided, so null string arguments would fail before or during serialization. Tests should cover ASCII, non-ASCII, empty strings, and malformed UTF-8 behavior if compatibility requires it.
