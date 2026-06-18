# sources/storage-engines/rocksdb/include/rocksdb/env_encryption.h

## Purpose

`env_encryption.h` declares the public encryption wrapper interfaces for storing RocksDB files encrypted at rest. It provides factories for an encrypted `Env` or encrypted `FileSystem`, cipher abstractions, an encryption provider contract, encrypted file wrappers, and an encrypted filesystem base class.

## Important APIs, types, and functions

Top-level factories are `NewEncryptedEnv(base_env, provider)` and `NewEncryptedFS(base_fs, provider)`. `BlockAccessCipherStream` defines random-access block encryption with `BlockSize`, `Encrypt`, `Decrypt`, protected `AllocateScratch`, `EncryptBlock`, and `DecryptBlock`. `BlockCipher : public Customizable` defines fixed-block `Encrypt`/`Decrypt`, `CreateFromString`, and a test-only `NewROT13Cipher`. `EncryptionProvider : public Customizable` creates per-file streams and prefixes through `GetPrefixLength`, `CreateNewPrefix`, `AddCipher`, `CreateCipherStream`, and optional `GetMarker`.

Encrypted wrappers include `EncryptedSequentialFile`, `EncryptedRandomAccessFile`, `EncryptedWritableFile`, and `EncryptedRandomRWFile`, all holding an underlying FS file plus a `BlockAccessCipherStream` and prefix length. `EncryptedFileSystem` extends `FileSystemWrapper` and exposes `AddCipher`.

## Control flow and behavior

On file creation, the provider creates a prefix and a cipher stream. Reads and writes are translated from logical user offsets to underlying file offsets after the encryption prefix. The sequential wrapper tracks `offset_` starting at `prefixLength_`; `Skip` and `Read` advance around encrypted payload offsets. Random-access reads, positioned writes, cache invalidation, range sync, preallocation, truncate, and file size all need prefix adjustment. The base `BlockAccessCipherStream` supports multi-block and partial-block encryption by dispatching to block-level methods with scratch storage.

## State and persistence

The persistent state added by encryption is the file prefix, which stores encryption options and usually aligns to page size for performance. Providers also hold cipher descriptors and read/write key state through `AddCipher`. File sizes visible to RocksDB exclude the prefix, while underlying persisted bytes include it. Durability is delegated to the wrapped filesystem's `Flush`, `Sync`, `Fsync`, and `Close`.

## Dependencies and integration points

The header depends on `Customizable`, `Env`, `FileSystem`, `Status`, and `Slice`. It integrates with RocksDB file creation and opening through `EnvOptions` and `FileOptions`, with the customization registry through `CreateFromString`, and with storage backends through `FileSystemWrapper`. It is designed to layer encryption without requiring table or DB code to understand encrypted bytes.

## Risks and test signals

Offset translation is the highest-risk behavior: prefix length must be consistently added for reads, writes, preallocation, truncation, and cache invalidation. The provider must preserve key compatibility for existing files, and `GetMarker` must not create false positives. The ROT13 cipher is explicitly test-only. Tests should cover partial block encryption, positioned reads/writes across block boundaries, prefix persistence and reopening, file size adjustment, unsupported `GetFileSize` fallback on encrypted random access files, key rotation/addition, and crash-safe flush/sync delegation.
