# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CertificateStore.java

## Purpose

`CertificateStore` defines the persistent certificate database operations needed by the default CA while avoiding a hard dependency from common HDDS code back into SCM implementation classes.

## Important APIs, Types, and Functions

It extends `SCMHandler` and defaults `getType()` to `SCMRatisProtocol.RequestType.CERT_STORE`. `storeValidCertificate` is annotated with `@Replicate(invocationType = CLIENT)`. Other methods include `storeValidScmCertificate`, `checkValidCertID`, `removeAllExpiredCertificates`, `getCertificateByID`, `listCertificate`, and `reinitialize`.

## Control Flow

The CA checks serial uniqueness, stores issued certificates by role, lists certificates for API calls, removes expired entries, and rebinds to a new `SCMMetadataStore` during SCM state reload.

## State and Persistence Behavior

This is the main persistence boundary for issued certificates. Ratis replication annotations signal operations that must be replicated in SCM HA.

## Dependencies and Integration Points

It integrates Java `X509Certificate`, serial `BigInteger`, protobuf `NodeType`, SCM HA handling, replication metadata, and SCM metadata DB abstractions.

## Risks and Edge Cases

Implementations must keep serial uniqueness atomic with storage. Role-specific listing must define ordering and pagination semantics. HA replication behavior is critical for certificate consistency across SCM nodes.

## Test Signals

Tests should cover duplicate serial rejection, valid certificate storage/listing per role, SCM certificate storage, expired certificate removal, Ratis replication invocation, and reinitialize behavior after metadata checkpoint restore.
