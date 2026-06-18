# sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_pkcs11_helper.c

Purpose: PKCS#11 smart-card/token key module using pkcs11-helper and OpenSSL X.509/RSA APIs.

Important APIs/functions: serialization/deserialization of `pkcs11h_data`, token/PIN prompt hooks, public-key extraction from certificate blobs, key signature generation, RSA encrypt/decrypt, certificate ID enumeration, key processing into eCryptfs keyring, provider/global/key decision graph transition functions, `.ecryptfsrc.pkcs11` parser, init/finalize, and `get_key_mod_ops()`.

Control flow: init sets pkcs11-helper log/token/PIN hooks, default protected auth, then parses `~/.ecryptfsrc.pkcs11` for global and provider settings. The key subgraph captures serialized certificate id, passphrase source, and optional X.509 PEM file. Processing creates a pkcs11-helper certificate, loads a certificate blob if needed, serializes module state, inserts a key module auth token, and pushes `ecryptfs_sig=<sig>`. Encryption uses the certificate public RSA key; decryption asks pkcs11-helper to decrypt with the token private key.

State/persistence: stores serialized PKCS#11 id, certificate DER blob, and passphrase in the key module blob. Reads user rc file for providers. PINs may come from callback or stored passphrase.

Dependencies/integration: pkcs11-helper, OpenSSL X509/RSA/BIO, libecryptfs decision graph/keyring, syslog, passwd home lookup.

Risks: RSA encryption uses `RSA_PKCS1_PADDING` rather than OAEP. Some allocations use `sizeof(*ctx)` where the intended struct is larger/different, suggesting memory sizing bugs in provider/key context allocation. Serialized blobs can contain passphrases. `.ecryptfsrc.pkcs11` parsing errors are mostly ignored in init.

Test signals: build with pkcs11-helper enabled, rc-provider parsing, token enumeration, PIN prompt callback, keyring insertion, and real token encryption/decryption.
