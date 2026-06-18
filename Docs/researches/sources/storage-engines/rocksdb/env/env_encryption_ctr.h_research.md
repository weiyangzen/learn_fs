# sources/storage-engines/rocksdb/env/env_encryption_ctr.h

## Purpose

`env_encryption_ctr.h` declares the CTR-mode encryption stream and provider used by RocksDB's encrypted file-system implementation. It is the public internal header that lets `env_encryption.cc`, factory code, tests, and external custom providers refer to the built-in CTR implementation without exposing its implementation details.

## Important APIs, types, and functions

- `CTRCipherStream final : public BlockAccessCipherStream` adapts a `BlockCipher` to the block-access stream interface using counter mode.
- `CTRCipherStream::BlockSize()` delegates to the wrapped cipher's block size.
- `CTRCipherStream::AllocateScratch()`, `EncryptBlock()`, and `DecryptBlock()` are protected overrides implemented in `env_encryption.cc`.
- `CTREncryptionProvider : public EncryptionProvider` owns the configured `BlockCipher` and creates CTR streams from file prefixes.
- `CTREncryptionProvider::kClassName()` returns `CTR`, the object-registry id.
- `GetPrefixLength()`, `CreateNewPrefix()`, `CreateCipherStream()`, and `AddCipher()` implement the provider contract.
- `PopulateSecretPrefixPart()` and `CreateCipherStreamFromPrefix()` are protected extension hooks for subclasses that want encrypted metadata in the prefix or custom stream construction.
- `NewEncryptedFileSystemImpl()` is declared here so built-in file-system registration can construct an encrypted FS without depending on private implementation classes.

## Control flow

Callers construct `CTREncryptionProvider` with either a cipher or no cipher. A provider without a cipher can later accept one through `AddCipher()`, or fail validation/stream creation if no cipher is configured. Creating a new encrypted file calls `CreateNewPrefix()`, which writes CTR parameters and any protected prefix data; opening an existing encrypted file calls `CreateCipherStream()` with the stored prefix. Both produce `BlockAccessCipherStream` instances, normally `CTRCipherStream`.

`CTRCipherStream` stores the shared cipher, a per-file IV string sized to the cipher block size, and the initial counter. For each block it derives a counter block from IV plus block index, encrypts that counter block with the cipher, and XORs it with file data. Decryption is the same operation as encryption.

## State and persistence behavior

The header defines the provider's default prefix length as 4096 bytes. That constant is part of the persistent layout because encrypted files reserve that many leading bytes before user data. `CTRCipherStream` itself keeps only runtime state: `cipher_`, `iv_`, and `initialCounter_`. The IV and initial counter are loaded from or generated into the prefix by the implementation file.

## Dependencies and integration points

The header depends on `rocksdb/env_encryption.h` for `EncryptionProvider`, `BlockAccessCipherStream`, `BlockCipher`, `EnvOptions`, `Slice`, and `Status`. It is included by `env_encryption.cc`, `file_system.cc`, and `env_test.cc`. `file_system.cc` needs it for `NewEncryptedFileSystemImpl()` during built-in file-system registration. Tests use `CTREncryptionProvider::kClassName()` and factory strings that target this provider.

## Risks and edge cases

- The constructor dereferences `c->BlockSize()` when copying the IV, so callers must never construct `CTRCipherStream` with a null cipher.
- The provider can be constructed without a cipher, which is useful for option loading but unsafe for actual encryption until prepared with a valid cipher.
- The header's comment says the CTR implementation is suitable only when the underlying `BlockCipher` is safe. The built-in test ROT13 cipher does not satisfy that condition.
- The 4096-byte prefix is performance-oriented for direct I/O alignment; changing it would affect on-disk compatibility and size accounting.

## Test signals

`env_test.cc` validates provider registry names and option parsing for `CTR`, `CTR://test`, `1://test`, and `id=CTR; cipher=ROT13`. `CreateEncryptedFileSystem` validates use through `FileSystem::CreateFromString()`. Encryption-specific behavior is otherwise mostly exercised through wrapper integration rather than a standalone CTR-mode unit in this subset.
