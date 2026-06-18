# sources/user-network-fs/impacket/tests/misc/test_dpapi.py

Purpose: Tests DPAPI parsing/decryption helpers for system keys, master keys, credentials, protected blobs, and Windows Vault files.

Important APIs, types, and functions: Uses `DPAPI_SYSTEM`, `MasterKeyFile`, `MasterKey`, `CredentialFile`, `DPAPI_BLOB`, `CREDENTIAL_BLOB`, `VAULT_VPOL`, `VAULT_VPOL_KEYS`, `VAULT_VCRD`, `VAULT_KNOWN_SCHEMAS`, `AES`, `HMAC`, `MD4`, and `SHA1`. Includes `dpapi_protect` ctypes helper for Windows-only blob generation.

Control flow: Tests parse static binary fixtures embedded as byte literals, decrypt master keys and blobs with known keys/entropy, derive user keys, decrypt vault policy/credential data, and skip live Windows protection outside Windows.

State and persistence behavior: Uses embedded fixture bytes and in-memory crypto. `dpapi_protect` calls Windows CryptoAPI only in the skipped Windows-specific test.

Dependencies and integration points: Integrates DPAPI structures with PyCryptodome primitives and Windows credential/vault schema parsing.

Risks: Large embedded vectors are hard to audit and brittle to structure changes. `atest_adminMasterKeyFile` is intentionally not discovered because it is prefixed `atest`.

Test signals: Strong signal for DPAPI_SYSTEM parsing, master key decryption, credential blob username extraction, optional entropy handling, VPOL key extraction, and VCRD schema decryption.
