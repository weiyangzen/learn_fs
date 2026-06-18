# Research: sources/storage-engines/tikv/components/test_util/data/generate_certs.sh

## sources/storage-engines/tikv/components/test_util/data/generate_certs.sh

Purpose: regenerates TLS fixture certificates for `test_util` security tests. It writes CA key/cert and server key/CSR/cert into the script directory.

Control flow is strict Bash with `set -euo pipefail`. It resolves its own path, derives output filenames, sets 3650-day validity and 2048-bit RSA keys, generates a CA private key and self-signed CA cert with critical CA constraints/key usages, prints it, generates a server key and CSR with CN `tikv-server`, CA false constraints, digital signature/key encipherment, server/client auth EKUs, SANs for `172.16.5.40` and `127.0.0.1`, signs it with the CA using copied extensions, then prints the server cert.

State and persistence are the generated `ca.key`, `ca.pem`, `key.pem`, `server.csr`, `server.pem`, and CA serial file created by OpenSSL. Dependencies are Bash, `realpath`, `dirname`, and OpenSSL with `-addext`/`-copy_extensions` support.

Risks include overwriting existing fixtures, OpenSSL version compatibility, long-lived static test keys, and SAN values becoming insufficient for new tests. Test signals are `security.rs` successfully loading these certs and grpcio channels accepting the generated credentials.
