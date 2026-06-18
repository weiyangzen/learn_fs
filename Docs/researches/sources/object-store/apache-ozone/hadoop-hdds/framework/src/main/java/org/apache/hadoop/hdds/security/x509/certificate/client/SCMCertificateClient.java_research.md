# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/SCMCertificateClient.java

## Purpose

`SCMCertificateClient` is the SCM-specific certificate client used to bootstrap and maintain SCM subordinate CA material. It builds CA CSRs, obtains sub-CA certificates either from a leader/root CA or local primary root CA, refreshes CA certificates, and initializes a root CA server for primary SCM bootstrapping.

## Important APIs, Types, and Functions

`COMPONENT_NAME` points to the SCM sub-CA storage path. Constructors accept SCM ID, cluster ID, cert ID, hostname, primary-SCM flag, and save callback. `configureCSRBuilder` sets subject from `SCM_SUB_CA_PREFIX + scmHostname`, SCM/cluster IDs, `CA=true`, and local key pair. `sign` is unsupported because SCM uses custom paths. Overridden `signAndStoreCertificate` calls `getSCMCertChain(..., true)` and stores subordinate/root material. `refreshCACertificates` runs `RefreshCACertificates`, which fetches leader root CAs and stores unknown certs. `recoverStateIfNeeded` chooses primary self-signed or root-signed certificate acquisition. `initializeRootCertificateServer` creates `DefaultCAServer`.

## Control Flow

On `GETCERT`, non-primary SCM requests a chain from SCM security RPC; primary SCM creates/initializes a root CA server, signs its own sub-CA CSR through that server, stores root and sub-CA material, persists the serial ID, and leaves renewer service disabled.

## State and Persistence Behavior

It inherits filesystem key/cert caches and adds SCM ID, cluster ID, hostname, primary flag, refresh executor, and save callback. It persists sub-CA certificates both via `storeCertificate` and a direct write to the component certificate filename expected by sub-CA server code.

## Dependencies and Integration Points

It integrates SCM security RPC, `DefaultCAServer`, `DefaultCAProfile`, `CertificateStore`, `CertificateCodec`, Ozone constants, `HddsUtils.threadNamePrefix`, and SCM node protobufs.

## Risks and Edge Cases

`signAndStoreCertificate` catches `Throwable` and rethrows runtime errors. `getPrimarySCMSelfSignedCert` catches `InterruptedException` with other exceptions and always interrupts the thread, even for non-interrupt failures. CA storage uses `CAType.SUBORDINATE` for root PEMs in some SCM flows because SCM treats root CA as CA cert, which can confuse naming expectations.

## Test Signals

Cover primary and non-primary bootstrap, CSR fields with CA=true, unsupported `sign`, root CA server initialization, cert ID callback, refresh of newly discovered leader roots, no-op refresh when unchanged, executor close, and storage filenames for sub-CA/root material.
