# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/CleanExpiredCertsSubcommand.java

## Purpose
Implements `ozone admin cert clean`, removing expired certificates from SCM metadata.

## Important APIs, Types, And Functions
The command extends `ScmCertSubcommand` and implements `execute(SCMSecurityProtocol)`. It calls `removeExpiredCertificates()` and prints the returned PEM list using `printCertList`.

## Control Flow
`ScmCertSubcommand.call()` creates the SCM security client, then this command removes expired certificates and formats the certificates that were removed.

## State And Persistence
The command mutates SCM certificate metadata by deleting expired certificate entries. Local state is not persisted.

## Dependencies And Integration Points
Depends on `SCMSecurityProtocol.removeExpiredCertificates`, `CertificateCodec` indirectly through `printCertList`, and SCM security client creation through `ScmOption`.

## Risks And Test Signals
The output says "List of removed expired certificates" even when none are removed. Tests should cover empty result, malformed returned PEM entries, security authorization failure, and that only expired certificates are removed server-side.
