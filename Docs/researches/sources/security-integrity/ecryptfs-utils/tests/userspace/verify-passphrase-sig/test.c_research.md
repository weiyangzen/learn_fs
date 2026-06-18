## sources/security-integrity/ecryptfs-utils/tests/userspace/verify-passphrase-sig/test.c

Purpose: C helper that validates libecryptfs passphrase signature and FEKEK derivation against expected hex outputs. It is the executable backend for `verify-passphrase-sig.sh`.

Important APIs and functions: `usage`, `main`, `from_hex`, `generate_passphrase_sig`, `to_hex`, `strcmp`. Control flow validates five arguments and exact hex lengths, zeroes buffers, decodes salt, calls `generate_passphrase_sig`, converts FEKEK to hex, and returns `EINVAL` if either signature or key material differs.

State and persistence: Sensitive key buffers are stack-allocated and not explicitly wiped after use. Dependencies are libecryptfs constants/functions. Integration is with automake `check_PROGRAMS` and the shell vector runner. Risks include strict buffer-size assumptions based on libecryptfs constants; the test is deterministic and gives strong compatibility signal for KDF/signature behavior but not for keyring integration.
