# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/DNCertificateClient.java

## Purpose

`DNCertificateClient` is the datanode-specific certificate client. It supplies datanode identity in CSRs and calls the SCM security protocol endpoint for datanode certificate chains.

## Important APIs, Types, and Functions

The constructor passes component `dn`, datanode thread prefix, cert ID save callback, and shutdown callback to `DefaultCertificateClient`. `configureCSRBuilder` sets `CA=false`, key pair from local keys, current security config, and subject as current short user plus local canonical host. `sign` calls `SCMSecurityProtocolClientSideTranslatorPB.getDataNodeCertificateChain(dnProto, csrPem)`.

## Control Flow

Initialization and renewal are inherited. When a cert is needed, the subclass builds a DN CSR and delegates signing to SCM using the datanode protobuf identity.

## State and Persistence Behavior

It adds immutable datanode details. Key/cert persistence, renewal directory swaps, and cert ID persistence callbacks are inherited.

## Dependencies and Integration Points

It integrates `DatanodeDetails`, UGI, local hostname resolution, `CertificateSignRequest`, SCM security protocol, and default certificate-client storage.

## Risks and Edge Cases

Hostname or current-user lookup failures abort CSR creation. The subject uses local runtime hostname, which must match expectations for certificate consumers. `new KeyPair(getPublicKey(), getPrivateKey())` assumes both keys are already available.

## Test Signals

Tests should cover CSR subject construction, CA flag false, key pair propagation, SCM RPC invocation with datanode details, hostname/UGI failure wrapping, and inherited init/renewal behavior for DN component paths.
