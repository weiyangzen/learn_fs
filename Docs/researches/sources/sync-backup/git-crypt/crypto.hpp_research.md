# sources/sync-backup/git-crypt/crypto.hpp

Purpose: public crypto abstraction for git-crypt, declaring initialization, AES block/CTR classes, HMAC-SHA1 state, and random byte generation.

Important APIs/types/functions: `init_crypto`, `struct Crypto_error`, `class Aes_ecb_encryptor`, `class Aes_ctr_encryptor`, `typedef Aes_ctr_decryptor`, `class Hmac_sha1_state`, and `random_bytes`. Constants expose AES key length, HMAC key length, block length, nonce length, and `MAX_CRYPT_BYTES`.

Control flow: no direct runtime flow in the header; it defines object lifecycles for crypto operations implemented in `crypto.cpp` and `crypto-openssl-11.cpp`.

State/persistence behavior: classes encapsulate key schedules, counters, pads, and HMAC contexts using private implementation structs and `unique_ptr` where OpenSSL types are hidden.

Dependencies/integration: includes `key.hpp` for key-length constants and standard headers. Consumed by command filtering, key generation, and CLI initialization.

Risks/test signals: header constants define file format/security limits, especially 12-byte nonce and 32-bit block counter. ABI/source compatibility relies on implementation files matching the declarations.
