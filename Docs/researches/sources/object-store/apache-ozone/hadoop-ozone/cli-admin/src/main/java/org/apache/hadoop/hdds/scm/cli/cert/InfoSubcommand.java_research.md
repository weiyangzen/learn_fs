# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/InfoSubcommand.java

## Purpose
Implements `ozone admin cert info`, printing details for one certificate serial ID.

## Important APIs, Types, And Functions
The command takes a required `serialId` parameter, calls `SCMSecurityProtocol.getCertificate(serialId)`, checks non-null with `Objects.requireNonNull`, parses PEM with `CertificateCodec.getX509Certificate`, and prints the `X509Certificate`.

## Control Flow
The command fetches the PEM string from SCM, prints the requested ID, then converts and prints certificate details. Certificate parse failures are logged to stderr and rethrown as `IOException`.

## State And Persistence
No local or cluster state is changed; it reads certificate metadata from SCM.

## Dependencies And Integration Points
Depends on SCM security protocol, Java X509 APIs, and Ozone certificate codec.

## Risks And Test Signals
Missing certificates become `NullPointerException` via `requireNonNull`, which may be less CLI-friendly than a checked error. Tests should cover found, not found, invalid PEM, and authorization failure cases.
