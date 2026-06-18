<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestCertificateSignRequest.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestCertificateSignRequest.java

Purpose: validates `CertificateSignRequest` builder output, CSR subject formatting, public key embedding, extensions, SAN handling, service-ID encoding, invalid argument rejection, and CSR PEM serialization.

Important APIs/types/functions: `CertificateSignRequest.Builder`, `build`, `generateCSR`, `getEncodedString`, `getCertificationRequest`, `getDistinguishedNameFormat`, `getPkcs9Extensions`, `SecurityConfig`, `HDDSKeyGenerator`, Bouncy Castle `PKCS10CertificationRequest`, `Extensions`, `Extension.keyUsage`, `Extension.subjectAlternativeName`, and `JcaContentVerifierProviderBuilder`.

Control flow: tests build CSRs from generated key pairs with subject/SCM/cluster/service identifiers and optional IP/DNS SAN entries. They inspect CSR subject, embedded `SubjectPublicKeyInfo`, extension attributes, criticality, and signature validity. Invalid-parameter tests omit required fields or use invalid dates/subjects, assert exceptions, then complete a valid request. Serialization writes a CSR to PEM and reconstructs it for equality.

State and persistence behavior: no durable store is used beyond transient temp metadata configuration. CSR state is immutable output from the builder and serialized/deserialized through PEM strings.

Dependencies and integration points: integrates Ozone security config, HDDS key generation, Bouncy Castle CSR and ASN.1 extension parsing, and Java key-pair verification.

Risks: distinguished-name ordering and escaping depend on X.500 formatting rules. Extension criticality, SAN representation, and service-ID OID encoding are interoperability-sensitive with SCM certificate signing.

Test signals: asserts subject DN equality, public-key equality, exactly one PKCS#9 extension attribute, critical key-usage/SAN extensions, absent SAN when not configured, valid CSR signatures, expected builder exceptions, service-ID OID/value, and serialized CSR equality.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/utils/TestCertificateSignRequest.java -->
