# sources/user-network-fs/libsmb2/lib/aes_apple.c

Purpose: Provides the Apple-specific AES-128 ECB block encrypt backend using CommonCrypto, compiled only when `__APPLE__` is defined.

Important APIs/functions: `AES128_ECB_encrypt_apple(const uint8_t *input, const uint8_t *key, uint8_t *output)` creates a CommonCrypto `CCCryptorRef` with `kCCEncrypt`, `kCCAlgorithmAES`, and `kCCOptionECBMode`, encrypts exactly one 16-byte block via `CCCryptorUpdate`, then releases the cryptor.

Control flow: The file includes its own header, enters the Apple-only block, creates a cryptor, returns silently on `CCCryptorCreate` failure, performs one update, and releases the cryptor. It does not finalize because it handles exactly one ECB block.

State/persistence: No persistent state. The cryptor is per call. Output is caller-owned and may remain unchanged if cryptor creation fails or update fails.

Dependencies/integration: Integrated through `aes.c`, which calls `AES128_ECB_encrypt_apple` on Apple and `AES128_ECB_encrypt_reference` elsewhere. Used transitively by AES-CCM and SMB2 signing code that call `AES128_ECB_encrypt`.

Risks: The source file has an unusual `AES_APPLE_H_` guard around the implementation; it does not break normal compilation but is stylistically misleading. Errors from `CCCryptorUpdate` and `dataOutMoved` are ignored. Silent failure can produce bad signatures/MACs without an immediate error path.

Test signals: Apple CI should compare this backend against reference AES vectors and AES-CCM vectors. Fault-injection or wrapper tests should verify that failure to create/update a cryptor is detectable at higher MAC verification layers.
