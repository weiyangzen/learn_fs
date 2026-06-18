# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmX509CertificateCodec.java

Purpose: verifies SCM HA certificate argument encoding for valid X.509 certificates and malformed bytes.

Important APIs and types: `initSecurityProvider()` initializes Ozone security providers through `SecurityConfig.initSecurityProvider(new OzoneConfiguration())`. `codec()` uses `KeyStoreTestUtil.generateKeyPair("RSA")` and `generateCertificate(...)`, serializes with `ScmX509CertificateCodec`, deserializes, and asserts certificate equality. `testCodecError()` wraps the UTF-8 bytes of `dummy` with protobuf `UnsafeByteOperations` and expects `InvalidProtocolBufferException`.

Control flow: JUnit `@BeforeAll` sets security providers once. The valid path exercises a real generated RSA certificate; the invalid path exercises defensive decoding and exception translation.

State and persistence: no filesystem persistence, but it depends on JVM crypto/security provider setup. The codec stores certificate material in protobuf `ByteString` during the test.

Integration points and risks: this protects SCM HA Ratis payloads for certificate-bearing APIs such as CA/certificate store replication. Coverage is good for basic DER/PEM handling but does not test multiple algorithms, certificate chains, expired certs, or null values. Crypto provider initialization is a common environmental risk if test order or provider availability changes.
