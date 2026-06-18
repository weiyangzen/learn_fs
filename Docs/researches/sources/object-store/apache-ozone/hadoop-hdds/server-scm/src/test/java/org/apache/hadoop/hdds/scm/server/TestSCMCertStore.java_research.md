# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMCertStore.java

## Purpose
`TestSCMCertStore` validates SCM certificate-store listing and expired-certificate removal. It ensures valid certificates can be stored and listed by role, and expired entries are removed while non-expired entries remain.

## Important APIs, Types, and Functions
- `SCMCertStore.Builder`, `storeValidCertificate`, `listCertificate`, and `removeAllExpiredCertificates` are tested.
- `SCMMetadataStoreImpl` provides the backing metadata store.
- A mocked `SCMRatisServer` returns the underlying invoker implementation to bypass HA proxying.
- `generateX509Cert` and `CertificateTestUtils.createSelfSignedCert` create certificates.

## Control Flow
Setup creates a temp metadata directory, security config, RSA key pair, SCM metadata store, and SCM cert store. Listing test stores SCM, OM, and datanode certificates, then checks list sizes. Expiration test stores expired and non-expired SCM/non-SCM certs, checks list sizes before cleanup, runs removal, and checks counts after cleanup.

## State and Persistence Behavior
Certificates are persisted in SCM metadata tables through `SCMCertStore`. Key directory creation mirrors expected security layout. The test closes the metadata store after each run.

## Dependencies and Integration Points
The file integrates certificate generation, SCM metadata, Ratis invoker proxying, and node-type role filtering. It documents current behavior where listing OM certs returns all valid certs, not only OM.

## Risks and Edge Cases
Covered risks include multiple certs with increasing counts, role-specific SCM listing, current broad OM/DN listing behavior, and expiration cleanup across SCM and non-SCM certificates. Pagination beyond a small limit is not tested.

## Test Signals
The list-size checks before and after cleanup provide a direct regression signal for certificate persistence and expired removal.
