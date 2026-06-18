<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestCertificateCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestCertificateCodec.java

Purpose: tests certificate encoding/decoding and filesystem round trips in `CertificateCodec`, including PEM strings, certificate paths, prepending certificates, and default component certificate files.

Important APIs/types/functions: `CertificateCodec`, `getPEMEncodedString`, `getX509Certificate`, `getCertPathFromPemEncodedString`, `prependCertToCertPath`, `writeCertificate`, `getTargetCert`, `getCertPath`, `SelfSignedCertificate`, `SecurityConfig`, and Java `CertificateFactory`/`CertPath`.

Control flow: a temp metadata directory is configured for each test. Tests generate self-signed certificates, serialize them to PEM, parse them back, build and decode `CertPath` instances, prepend one cert ahead of another, write PEM and default certificate files, force-rewrite a named certificate, and read multi-cert paths back in order.

State and persistence behavior: files are written under either a supplied base path or the codec's configured component directory. The tests validate content by serial number and object equality, and they check that repeated writes to the same filename are supported.

Dependencies and integration points: uses Ozone `SecurityConfig`, certificate generation utilities, Guava immutable lists for cert paths, JCA certificate factories, and JUnit temp directories.

Risks: certificate path ordering matters; regressions in PEM boundary formatting, newline handling, or overwrite semantics can break interoperability with external tools and other Ozone certificate clients.

Test signals: asserts PEM begin/end markers, X.509 equality after parse, `CertPath` order after encode/decode, prepended certificate ordering, non-null loaded certs, matching serial numbers, and multi-certificate reread order.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestCertificateCodec.java -->
