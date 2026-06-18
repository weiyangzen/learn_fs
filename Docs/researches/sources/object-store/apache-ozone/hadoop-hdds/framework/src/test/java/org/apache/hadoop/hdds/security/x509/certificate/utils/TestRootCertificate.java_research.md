<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestRootCertificate.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestRootCertificate.java

Purpose: tests `SelfSignedCertificate` root/non-root certificate generation, distinguished-name content, validity windows, CA basic constraints, fixed root serial behavior, certificate verification, and invalid builder input handling.

Important APIs/types/functions: `SelfSignedCertificate.Builder`, `makeCA`, `build`, `SecurityConfig`, `HDDSKeyGenerator`, `CertificateCodec`, `getPEMEncodedString`, `getTargetCert`, `X509Certificate.verify`, and the basic-constraints extension OID `2.5.29.19`.

Control flow: each test configures security metadata, generates a key pair, builds certificates with subject, SCM ID, cluster ID, validity bounds, and serial ID, then inspects issuer/subject and extensions. CA tests write and reread PEM through `CertificateCodec`. Invalid-param tests clear or invert required fields and expect `IllegalArgumentException`, then checks wrong-key verification fails while a corrected builder still builds.

State and persistence behavior: most state is transient certificate objects; the CA test persists a PEM certificate to a temp path and reloads it. The builder encodes certificate validity and CA flags directly into the generated X.509 object.

Dependencies and integration points: relies on Ozone security config, HDDS key generation, JCA certificate verification, and certificate codec persistence.

Risks: date comparisons can be clock-sensitive. DN formatting follows Java principal canonicalization, so expected strings must track principal behavior. CA basic constraints and root serial number are protocol-significant.

Test signals: asserts issuer equals subject for self-signed certs, dates are within requested bounds, DN content, non-CA basic constraints of `-1`, successful verification with the public key, CA basic constraints and critical extension presence, root serial `BigInteger.ONE`, PEM round trip, invalid builder exceptions, wrong-key verification failure, and valid final build.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestRootCertificate.java -->
