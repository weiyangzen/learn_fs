## sources/security-integrity/ecryptfs-utils/tests/lib/etl_add_passphrase_key_to_keyring.c

Purpose: Small C bridge exposing libecryptfs `ecryptfs_add_passphrase_key_to_keyring()` to shell tests. It converts a hex salt, adds a passphrase-based key to the kernel keyring, and prints the authentication token signature.

Important APIs and functions: `main`, `from_hex`, `ecryptfs_add_passphrase_key_to_keyring`, `printf`. Control flow validates exactly two arguments, decodes salt into `ECRYPTFS_SALT_SIZE`, calls libecryptfs, treats return code `1` (already in keyring) as success, prints the hex signature on success, and returns the library code otherwise.

State and persistence: Persists key material in the user keyring until tests unlink it; stack buffers hold salt and signature. Dependencies are libecryptfs headers/library and kernel keyring support. Integration is used by `etl_add_fekek_passphrase` and `etl_add_fnek_passphrase`. Risks include passphrase/salt shell-argument exposure and reliance on libecryptfs return-code convention.
