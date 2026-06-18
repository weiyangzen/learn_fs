# sources/user-network-fs/rclone/bin/make-test-certs.sh

Purpose: generates a local CA plus server and password-protected client TLS certificates for testing rclone servers with TLS and mutual TLS. Configuration is environment-driven (`OUT_DIR`, subjects, CNs, passwords, validity days).

Control flow creates OpenSSL extension configs, creates/reuses CA key, creates CA CSR/cert, creates server key/CSR/cert with localhost SAN, creates encrypted client key/CSR/cert with clientAuth EKU, verifies the chain, and prints example `rclone serve http` and client commands. State is written under `OUT_DIR`, including private keys and CSRs. Dependencies are bash and OpenSSL. Risks include predictable default client key password, overwriting server/client keys, generated CA trust scope, and shell-created OpenSSL config files. Test signal is `openssl verify` success plus manual rclone commands.
