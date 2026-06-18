# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/OldX509CertificateCodecForTesting.java

Purpose: singleton test-only legacy codec for persisted X.509 certificates, used to verify current certificate codec compatibility with older SCM metadata format.

Important APIs and types: implements `Codec<X509Certificate>`. `get()` returns the singleton instance. `toPersistedFormatImpl()` converts a certificate to PEM text with `CertificateCodec.getPEMEncodedString(object)` and UTF-8 bytes. `fromPersistedFormatImpl()` reconstructs a certificate through `CertificateCodec.getX509Certificate(rawData)`. `copyObject()` returns the same immutable certificate reference.

Control flow: encoding and decoding are straight-line calls into the certificate utility layer, with checked exceptions propagated according to the codec contract.

State and persistence: the singleton is stateless; the persisted representation is PEM-encoded certificate bytes. Dependencies include `CertificateCodec`, `SCMSecurityException`, Java security certificate types, and HDDS `Codec`.

Integration points and risks: `TestX509CertificateCodec` compares the new RocksDB metadata codec against this old codec for generated RSA certificates. Risk centers on preserving legacy PEM byte compatibility; changing this class would change the compatibility oracle rather than production behavior. It does not test certificate chains or private keys.
