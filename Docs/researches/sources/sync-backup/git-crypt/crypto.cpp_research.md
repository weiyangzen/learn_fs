# sources/sync-backup/git-crypt/crypto.cpp

Purpose: implementation of AES-CTR stream processing built on top of the AES-ECB block encryptor declared in `crypto.hpp`.

Important APIs/types/functions: `Aes_ctr_encryptor` constructor/destructor, `process`, and static `process_stream`. `Aes_ctr_decryptor` is a typedef to the same class because CTR encryption and decryption are symmetric.

Control flow: construction copies a 12-byte nonce into the first part of a 16-byte counter block and starts `byte_counter` at zero. `process` generates a new AES pad every 16 bytes by storing the block counter in big-endian form into the last 4 bytes, encrypting the counter block, and XORing input bytes with pad bytes. Counter wrap throws a `Crypto_error`. `process_stream` reads chunks from an input stream, processes in place, and writes to output.

State/persistence behavior: state is the fixed nonce, rolling 32-bit byte counter, current counter block, and current pad. The destructor clears the pad. No persistent storage is used.

Dependencies/integration: depends on `Aes_ecb_encryptor`, `store_be32`, stream I/O, and `Crypto_error`. Used by `commands.cpp` for file clean/smudge/diff.

Risks/test signals: counter limit enforcement is essential because nonce/counter reuse breaks CTR security. Tests should verify known-vector behavior, chunk-boundary equivalence, in-place processing, decryption symmetry, and error on maximum byte counter wrap.
