# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_encrypted_secrets.c

Purpose: This cmocka file directly includes `../encrypted_secrets.c` under `TEST_ENCRYPTED_SECRETS` and validates encrypted secret handling for Samba's secrets database module. It covers key-file loading, AES-GCM value encryption/decryption, tamper detection, message-level secret-attribute encryption/decryption, header validation, and rejection of unencrypted secret attributes.

Important APIs, types, and functions: The tests exercise `es_init`, `gnutls_encrypt_aead`, `gnutls_decrypt_aead`, `decrypt_value`, `encrypt_secret_attributes`, `decrypt_secret_attributes`, `check_header`, and `makeEncryptedSecret`. They use `struct es_data`, `struct EncryptedSecret`, `struct PlaintextSecret`, LDB messages/elements, `DATA_BLOB`, and constants such as `SECRETS_KEY_FILE`, `DSDB_SECRET_ATTRIBUTES`, `ENCRYPTED_SECRET_MAGIC_VALUE`, `SECRET_ATTRIBUTE_VERSION`, and `ENC_SECRET_AES_128_AEAD`.

Control flow: `setup` creates a temporary LDB module chain with an `eol` module, connects a local TDB database, and removes stale db/lock/key files. `setup_with_key` writes a 16-byte key file, inserts `@SAMBA_DSDB` required-feature metadata, and initializes the module. Key tests verify absent, exact-length, short, and long key files. Crypto tests decrypt a known static ciphertext, encrypt a value and NDR-decode the `EncryptedSecret`, then decrypt it. Tamper tests mutate header flags, ciphertext, and IV and expect `LDB_ERR_OPERATIONS_ERROR`. Message tests encrypt all `DSDB_SECRET_ATTRIBUTES`, confirm normal attributes remain plaintext, then decrypt back to original values.

State and persistence behavior: The tests create and delete `apitest.ldb`, its lock file, and the secrets key file named by `SECRETS_KEY_FILE`. Module private state stores loaded keys, `encrypt_secrets`, and encryption algorithm. Encrypted message data is transient, but the tests model how the real module would persist encrypted secret attribute values in LDB.

Dependencies and integration points: The file mocks `dsdb_module_search_dn` and `dsdb_module_reference_dn` so initialization sees the encrypted-secrets required feature without a full DSDB. It depends on GnuTLS AEAD behavior, NDR marshalling, Samba LDB module APIs, and talloc ownership.

Risks: Key-file handling is security critical: short keys must fail, long keys are truncated to the first 16 bytes, and absent keys disable encryption. Any change in NDR wire layout, header constants, or AEAD algorithm will require test updates and migration consideration. Rejecting unencrypted secret attributes is a compatibility/security boundary.

Test signals: Passing tests show key loading is deterministic, encrypted values round-trip, malformed encrypted records fail, secret attributes are redacted by encryption while normal attributes stay readable, and static encrypted records remain decryptable with the expected key.
