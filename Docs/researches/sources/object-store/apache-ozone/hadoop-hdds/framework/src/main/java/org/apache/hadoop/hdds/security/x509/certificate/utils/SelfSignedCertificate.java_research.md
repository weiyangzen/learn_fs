# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/SelfSignedCertificate.java

## Purpose

`SelfSignedCertificate` builds a self-signed X.509 certificate, primarily for bootstrapping an Ozone root CA when no external CA certificate is configured.

## Important APIs, Types, and Functions

`newBuilder` returns the nested builder. `generateCertificate` converts the public key to `SubjectPublicKeyInfo`, creates a `ContentSigner`, chooses the serial ID from CA serial or monotonic time, builds a subject/issuer name with serial number, creates `X509v3CertificateBuilder`, and adds CA basic constraints, key usage, and SAN extensions when `makeCA` was used. Builder methods set subject, SCM ID, cluster ID, validity dates, key pair, config, CA serial, and SANs from DNS/IP/current host.

## Control Flow

Builder validation requires key, nonblank subject/cluster/SCM IDs, begin date before end date, and duration no longer than configured max. `build` creates the certificate object and delegates to BouncyCastle signing/conversion.

## State and Persistence Behavior

No files are written here. The generated `X509Certificate` is returned to callers such as `DefaultCAServer`, which writes it through `CertificateCodec`.

## Dependencies and Integration Points

It integrates `SecurityConfig`, BouncyCastle X.509 builders, `CertificateSignRequest` DN format, Ozone certificate exceptions, domain/inet utilities, and Hadoop `Time.monotonicNow`.

## Risks and Edge Cases

When no CA serial ID is supplied, the serial comes from monotonic time and is not globally durable. SANs are only added in the CA-serial path. `beginDate`/`endDate` are dereferenced without explicit null checks, so missing dates produce null-pointer failures.

## Test Signals

Cover successful CA certificate creation, max-duration rejection, invalid date order, missing fields, SAN encoding, fixed serial ID, self-signed issuer/subject equality, basic constraints/key usage presence, and generated certificate verification with its public key.
