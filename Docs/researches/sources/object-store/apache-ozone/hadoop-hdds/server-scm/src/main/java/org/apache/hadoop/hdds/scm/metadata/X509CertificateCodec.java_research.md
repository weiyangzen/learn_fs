# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/X509CertificateCodec.java

Purpose: RocksDB metadata codec for `X509Certificate` values stored in SCM certificate tables.

Important APIs and types: Singleton `Codec<X509Certificate>` with codec-buffer support. Methods include `toCodecBuffer`, `fromCodecBuffer`, `toPersistedFormat`, `fromPersistedFormat`, `copyObject`, and `supportCodecBuffer`.

Control flow: Writes certificates as PEM through `CertificateCodec.writePEMEncoded` into a `LengthOutputStream` and codec buffer. Reads parse PEM bytes using `CertificateCodec.readX509Certificate`. Raw byte persistence delegates through heap codec buffers or `ByteArrayInputStream`.

State and persistence behavior: Stateless singleton. Defines durable value format for `validCerts` and `validSCMCerts` tables.

Dependencies and integration points: Used by `SCMDBDefinition` certificate column families and SCM certificate stores. Separate from HA message `ScmX509CertificateCodec`.

Risks and test signals: PEM parser/writer compatibility and codec-buffer lifecycle are important. Tests should cover round trips, malformed PEM, buffer allocation paths, copy identity, and compatibility with existing certificate table entries.
