# sources/storage-engines/tikv/components/encryption/src/io.rs

Purpose: Provides transparent encrypting/decrypting `Read`, `Write`, `Seek`, `AsyncRead`, and `AsyncWrite` adapters for TiKV file I/O. It implements AES/SM4 CTR stream encryption while preserving random-access semantics by resetting the counter from byte offsets.

Important APIs and types: Public wrappers are `EncrypterReader`, `DecrypterReader`, `EncrypterWriter`, and `DecrypterWriter`. `create_aes_ctr_crypter` maps `EncryptionMethod` to OpenSSL ciphers. Internal `CrypterReader`, `CrypterWriter`, `CrypterCore`, and `AsyncWriteState` hold stream offset, OpenSSL crypter, reusable buffer, and pending async-write state.

Control flow: Plaintext method bypasses cryptography. Reads fill caller buffers then encrypt/decrypt in place. Seeks reset the core offset and lazily rebuild OpenSSL state. Writes encrypt into an internal buffer, write to the inner writer, and roll back the crypto offset on partial or failed writes. Async writes first encrypt into a buffer, then consume that buffer across polls until the encrypted bytes are written.

State and persistence behavior: No metadata is persisted here; state is per-stream. `CrypterCore::offset` advances only after successful cryptographic transformation. `reset_crypter` adjusts IV by block offset and consumes partial-block zeros so CTR keystream alignment matches random file offsets. `MAX_INPLACE_CRYPTION_SIZE` limits temporary buffer growth for in-place operations.

Dependencies and integration: Called by `DataKeyManager` when opening encrypted files and by other storage components that wrap file handles. It depends on OpenSSL, `file_system::File`, futures traits, `kvproto::EncryptionMethod`, and crate `Iv` validation.

Risks: Reader crypto errors panic because the underlying reader offset cannot be rolled back without wider API changes. Async write cancellation is guarded by a panic if another write tries to overwrite pending encrypted data. The implementation assumes CTR-mode update output length always equals input length; other modes would break invariants. SM4 support depends on the crate feature and linked OpenSSL support.

Test signals: Tests cover sync decrypt/read, encrypt-then-decrypt via readers and writers, random seeks and offsets, plaintext bypass, async read/write, injected async write failure, partial writes, and a should-panic case for aborted pending async writes.
