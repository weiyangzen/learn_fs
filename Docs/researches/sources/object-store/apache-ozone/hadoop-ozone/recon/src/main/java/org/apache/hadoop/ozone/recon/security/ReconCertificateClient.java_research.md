## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/security/ReconCertificateClient.java

Purpose: `ReconCertificateClient` specializes the default HDDS certificate client for the Recon component so Recon can request and renew certificates from SCM CA as a RECON node.

Important APIs and types: extends `DefaultCertificateClient`, defines `COMPONENT_NAME = "recon"`, stores cluster ID and Recon ID from `ReconStorageConfig`, overrides `configureCSRBuilder`, `sign`, and `getLogger`.

Control flow: `configureCSRBuilder` starts from the parent CSR builder, derives a subject from current short user and local canonical hostname, sets CA=false, attaches the current key pair and security config, and returns the builder. `sign` builds `NodeDetailsProto` with host name, cluster ID, Recon UUID, and node type RECON, then calls `getCertificateChain` on the SCM security client.

State and persistence: certificate serial persistence is delegated to `DefaultCertificateClient` through the constructor's current serial ID and `saveCertIdCallback`; `ReconStorageConfig` stores that serial ID. This class keeps only identity strings.

Dependencies and integration points: depends on `SCMSecurityProtocolClientSideTranslatorPB`, `SecurityConfig`, `ReconStorageConfig`, and Hadoop UGI. It is part of Recon's secure startup and certificate lifecycle.

Risks and edge cases: local hostname or UGI lookup failures become `CertificateException` with CSR error. The TODO notes certificate retrieval from multiple SCMs is not implemented. Subject format changes can affect certificate expectations. Stable Recon ID depends on storage metadata.

Test signals: no direct test was found. Tests should mock SCM security client signing, verify RECON node details, assert CSR subject/key/config fields, and cover hostname/UGI failure handling.
