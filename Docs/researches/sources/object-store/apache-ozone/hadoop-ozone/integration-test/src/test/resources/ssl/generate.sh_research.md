# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/ssl/generate.sh

Purpose: This helper script generates local SSL/TLS test materials: a CA key/certificate, server key/certificate/PKCS8 private key, and client key/certificate/PKCS8 private key for mutual TLS scenarios.

Important APIs and types: It is a shell script invoking `openssl genrsa`, `openssl req`, `openssl x509`, `openssl rsa`, and `openssl pkcs8`. Variables `SERVER_CN` and `CLIENT_CN` default to `localhost`. Generated files include `ca.key`, `ca.crt`, `server.key`, `server.csr`, `server.crt`, `server.pem`, `client.key`, `client.csr`, `client.crt`, and `client.pem`.

Control flow: The script creates a passphrase-protected CA key, self-signed CA cert, passphrase-protected server key, server CSR, CA-signed server certificate, unencrypted server key, passphrase-protected client key, client CSR, CA-signed client certificate, unencrypted client key, and PKCS8 PEM private keys.

State and persistence behavior: It writes key, CSR, certificate, and PEM files into the current working directory and overwrites existing files with the same names. Certificates are valid for 365 days and use serial `01` for both server and client certs.

Dependencies and integration points: It supports SSL test resources consumed by Ozone/HDDS tests that need certificate chains, trust cert collections, server private keys, and optional mutual-TLS client credentials.

Risks: Hard-coded passphrase `1111`, duplicate serial numbers, localhost CN, no subjectAltName, and overwriting behavior make this suitable only for tests. Modern TLS clients may require SANs instead of CN-only certificates.

Test signals: The expected signal is successful generation of all certificate and key artifacts with OpenSSL and their later loadability by SSL-enabled tests.
