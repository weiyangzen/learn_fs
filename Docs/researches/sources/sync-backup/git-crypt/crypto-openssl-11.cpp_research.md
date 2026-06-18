# sources/sync-backup/git-crypt/crypto-openssl-11.cpp

Purpose: OpenSSL-backed implementation of AES-ECB block encryption, HMAC-SHA1 state, crypto initialization, and random byte generation for git-crypt.

Important APIs/types/functions: `init_crypto`, `Aes_ecb_encryptor::Aes_impl`, `Aes_ecb_encryptor` constructor/destructor/`encrypt`, `Hmac_sha1_state::Hmac_impl`, HMAC constructor/destructor/`add`/`get`, and `random_bytes`.

Control flow: initialization loads OpenSSL error strings. AES construction calls `AES_set_encrypt_key`; encryption calls `AES_encrypt`. HMAC construction allocates `HMAC_CTX`, initializes with `EVP_sha1`, streams data via `HMAC_Update`, and finalizes via `HMAC_Final`. Random generation calls `RAND_bytes` and constructs a detailed OpenSSL error message on failure.

State/persistence behavior: key material is held in OpenSSL `AES_KEY` and HMAC context objects. The AES destructor explicitly zeroes the key schedule. No persistent state is stored.

Dependencies/integration: depends on OpenSSL AES, SHA/HMAC/EVP/RAND/ERR APIs and `explicit_memset`. `crypto.cpp` uses `Aes_ecb_encryptor` for CTR mode; `key.cpp` uses `random_bytes`.

Risks/test signals: these are low-level security primitives. Tests should cover AES-CTR round trips, HMAC deterministic output, random generation failure propagation where injectable, key material zeroing under review, and compatibility with current OpenSSL deprecation behavior.
