<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OMCertificateClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OMCertificateClient.java

Purpose: OM-specific certificate client built on `DefaultCertificateClient`. It creates certificate signing requests for OM nodes and asks SCM security service for OM certificate chains.

Important APIs/types/functions: Constructor wires `SecurityConfig`, SCM security translator, `OMStorage`, OM details proto, service ID, SCM ID, certificate ID save callback, and shutdown callback into the base client. `configureCSRBuilder` fills CA=false, current key pair, security config, SCM ID, cluster ID, subject, and optional service name. `sign` calls `getOMCertChain(omInfo, encodedCSR)`. `getLogger` returns the class logger.

Control flow: CSR creation starts from the base builder. If DNS names are available, subject becomes current short user plus hostname; otherwise it uses only hostname to avoid IP-only alt-name validation issues. The request is then logged and later submitted to SCM for signing.

State and persistence behavior: Holds service ID, SCM ID, cluster ID, and OM details. Certificate/key persistence is inherited from `DefaultCertificateClient` and callbacks backed by OM storage.

Dependencies and integration points: Integrates OM identity from `OMStorage`, SCM security protocol, HDDS certificate utilities, `UserGroupInformation`, and service-name support for HA. It participates in secure OM startup and certificate renewal flows.

Risks: Subject construction depends on current OS/Kerberos user and DNS-name detection. Empty service ID omits service-name SAN data, which may matter in HA/service-address validation. SCM signing failures surface as IO/security exceptions during startup or renewal.

Test signals: Tests should verify CSR fields for DNS and IP-only cases, service-name inclusion, cluster/SCM IDs, key pair wiring, and that `sign` calls SCM with OM details and encoded CSR.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/OMCertificateClient.java -->
