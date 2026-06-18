# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/ScmCertSubcommand.java

## Purpose
Provides the base class for certificate commands that connect to SCM security protocol and share certificate list formatting.

## Important APIs, Types, And Functions
`ScmCertSubcommand` implements `Callable<Void>`, mixes in `ScmOption`, declares abstract `execute(SCMSecurityProtocol)`, and provides `printCertList` and `printCert(X509Certificate)` using a fixed column format.

## Control Flow
`call()` creates an SCM security client, invokes subclass logic, and returns. `printCertList` prints an empty message or parses each PEM certificate and prints certificate fields, logging parse failures to stderr.

## State And Persistence
No state is persisted. The client may read or mutate certificate state depending on subclass.

## Dependencies And Integration Points
Used by `cert info`, `cert list`, and `cert clean`; depends on `SCMSecurityProtocol`, `CertificateCodec`, and Java X509 APIs.

## Risks And Test Signals
Unlike `ScmSubcommand`, the security client is not closed in this base class. Formatting uses wide fixed columns that can be awkward for long DNs. Tests should cover parse failures, empty lists, and client lifecycle expectations.
