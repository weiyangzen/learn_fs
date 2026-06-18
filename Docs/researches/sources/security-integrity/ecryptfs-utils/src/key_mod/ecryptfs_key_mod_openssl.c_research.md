# sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_openssl.c

Purpose: OpenSSL-backed public-key key module for eCryptfs, using PEM RSA private keys to wrap/unwrap session keys and generate key signatures.

Important APIs/functions: `ecryptfs_openssl_serialize/deserialize`, `ecryptfs_openssl_generate_signature`, key file mkdir/write/read helpers, `ecryptfs_openssl_get_key_sig`, `ecryptfs_openssl_generate_key`, `ecryptfs_openssl_encrypt`, `ecryptfs_openssl_decrypt`, decision-graph transition functions for keyfile/passphrase/passphrase-file, generation subgraph functions, `ecryptfs_openssl_init`, and `get_key_mod_ops()`.

Control flow: decision graph captures PEM key path and passphrase, serializes them into the key module blob, inserts the key module auth token into the keyring, pushes `ecryptfs_sig=<sig>` and a `max_key_bytes` option. Encryption/decryption re-read the RSA private key from the serialized path/passphrase and use RSA OAEP padding. Key generation writes a 1024-bit encrypted RSA private key under a suggested `~/.ecryptfs/pki/openssl/key.pem`.

State/persistence: persistent key material lives in the PEM key file. Runtime state includes serialized path/passphrase blob, suggested path strings, and mount option stack values. Passphrases are heap strings and not consistently zeroed before free.

Dependencies/integration: OpenSSL PEM/RSA/ERR/ENGINE APIs, syslog, passwd home lookup, decision graph, libecryptfs keyring APIs.

Risks: 1024-bit RSA is obsolete. OpenSSL APIs used are legacy. Serialized blobs contain passphrases. `tf_ssl_passwd_fd` returns `ENOSYS` without negation, likely inconsistent error semantics. File permissions rely on recursive mkdir mode and OpenSSL file write behavior.

Test signals: plugin build with OpenSSL enabled, key generation, keyring insertion, and mount with OpenSSL key module.
