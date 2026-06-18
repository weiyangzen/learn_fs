# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmX509CertificateCodec.java

Purpose: SCM HA codec for `X509Certificate` values, serializing certificates as PEM text.

Important APIs and types: Uses `CertificateCodec.getPEMEncodedString` and `CertificateCodec.getX509Certificate`; implements `ScmCodec<X509Certificate>`.

Control flow: Serialization converts the certificate to a PEM string, encodes UTF-8 bytes, and wraps them in shaded `ByteString`. Deserialization reads UTF-8 PEM text and parses an X.509 certificate. Any exception is converted to shaded `InvalidProtocolBufferException`.

State and persistence behavior: Stateless. HA messages carry PEM bytes; RocksDB certificate persistence uses a separate metadata codec.

Dependencies and integration points: Registered for certificate-store invocations and certificate list responses.

Risks and test signals: PEM formatting and certificate parser behavior define wire compatibility. Tests should cover round trips for generated certs, malformed PEM, serial number preservation, and distinction from metadata `X509CertificateCodec`.
