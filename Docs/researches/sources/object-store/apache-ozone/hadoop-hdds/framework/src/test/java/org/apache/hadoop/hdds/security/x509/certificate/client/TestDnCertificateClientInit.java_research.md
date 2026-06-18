<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/TestDnCertificateClientInit.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/TestDnCertificateClientInit.java

Purpose: parameterized initialization matrix for `DNCertificateClient`, validating how datanode certificate-client startup reacts to combinations of private key, public key, and certificate presence.

Important APIs/types/functions: `DNCertificateClient`, `CertificateClient.InitResponse`, `SUCCESS`, `GETCERT`, `FAILURE`, `KeyStorage.storePrivateKey`, `KeyStorage.storePublicKey`, `CertificateCodec.writeCertificate`, `OzoneSecurityUtil.checkIfFileExist`, and `SecurityConfig` key/certificate path helpers.

Control flow: `parameters()` supplies combinations of present/missing private key, public key, and certificate with expected init responses. `setUp` builds a fresh temp metadata tree, generates one RSA key pair and matching X.509 certificate, and constructs the DN client. Each parameterized test writes or deletes key/certificate files to match the case, invokes `dnCertificateClient.init()`, and validates both response and key-file recovery behavior for `GETCERT`.

State and persistence behavior: all state is persisted under the temporary HDDS metadata directory. Missing public keys may be regenerated from private-key material during `GETCERT` flows, while missing private keys or incompatible certificate states produce failure. The certificate file is intentionally deleted or written through `CertificateCodec`.

Dependencies and integration points: uses `OzoneConfiguration`, `SecurityConfig`, `HDDSKeyGenerator`, Hadoop test key/cert utilities, Apache Commons IO deletion, JUnit parameterization, and Ozone security utilities.

Risks: the test is compact but sensitive to exact init-state semantics. If init later performs additional repair or validation, expected responses in the matrix must change together with file-existence assertions.

Test signals: asserts the correct `InitResponse` for every matrix row and verifies that `GETCERT` paths leave private and public key files on disk.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/TestDnCertificateClientInit.java -->
