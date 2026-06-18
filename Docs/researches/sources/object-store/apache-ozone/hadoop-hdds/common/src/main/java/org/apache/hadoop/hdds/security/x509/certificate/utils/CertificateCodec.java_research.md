# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/CertificateCodec.java

## Purpose
Reads and writes X.509 certificates and certificate paths in PEM format for HDDS components.

## Important APIs and types
Static helpers encode `X509Certificate` or `CertPath` to PEM, parse a leading certificate from PEM bytes/string, parse full `CertPath`, return the first cert from a path, and obtain a Bouncy Castle X.509 `CertificateFactory`. Instance methods resolve a certificate location from `SecurityConfig`, write certificates using configured or explicit filenames, read certificate paths, prepend certificates to paths, and read target certificates.

## Control flow and state
Each instance stores `SecurityConfig`, a location path, and owner-only POSIX permissions. Writes create the base directory if missing, write UTF-8 PEM data, log the path and PEM string, and set owner read/write/execute permissions on the certificate file. Reads verify the base directory, require the named file to exist, and parse it as a PEM certificate path.

## Dependencies and integration points
Depends on Bouncy Castle `JcaPEMWriter` and provider `"BC"`, Java certificate APIs, `SecurityConfig`, and `SCMSecurityException`. Certificate clients, CA servers, and key/cert bootstrap code use it for PEM persistence.

## Risks and test signals
Tests should cover single-certificate and chain PEM parsing, prepend order, missing file errors, directory creation failure, permission setting on POSIX filesystems, behavior without Bouncy Castle provider, and error-code mapping for PEM encode failure. Logging full PEM certificates may be acceptable for public certs but should be reviewed for operational verbosity.
