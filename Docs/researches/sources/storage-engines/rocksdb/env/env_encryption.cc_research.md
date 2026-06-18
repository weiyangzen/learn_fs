# sources/storage-engines/rocksdb/env/env_encryption.cc

## Purpose

`env_encryption.cc` implements RocksDB's encrypted file-system adapter and the built-in CTR encryption provider used by that adapter. It wraps `FSSequentialFile`, `FSRandomAccessFile`, `FSWritableFile`, and `FSRandomRWFile` so callers see plaintext bytes at logical file offsets, while the underlying file system stores an optional provider prefix followed by encrypted data. It also registers built-in encryption/cipher factories (`CTR`, `CTR://test`, `1://test`, and `ROT13`) for `CreateFromString`-based configuration.

## Important APIs, types, and functions

- `EncryptionProvider::NewCTRProvider()` constructs a `CTREncryptionProvider` around a supplied `BlockCipher`.
- `EncryptedSequentialFile`, `EncryptedRandomAccessFile`, `EncryptedWritableFile`, and `EncryptedRandomRWFile` implement offset translation and call `BlockAccessCipherStream::Encrypt()` or `Decrypt()` around the wrapped file operations.
- `EncryptedFileSystemImpl` derives from `EncryptedFileSystem` and is the main `FileSystemWrapper` implementation. It owns a `std::shared_ptr<EncryptionProvider>` registered as option `provider`.
- `NewEncryptedFileSystemImpl()`, `NewEncryptedFS()`, and `NewEncryptedEnv()` are the construction entry points used by direct callers and the file-system factory registry.
- `BlockAccessCipherStream::Encrypt()` and `Decrypt()` provide block-granular encryption over arbitrary byte ranges, handling partial leading/trailing blocks by copying through a temporary full-block buffer.
- `ROT13BlockCipher` is a test/sample cipher registered as a `BlockCipher`. It is explicitly not production-safe.
- `CTRCipherStream` and `CTREncryptionProvider` implement CTR mode over an arbitrary `BlockCipher`.
- `BlockCipher::CreateFromString()` and `EncryptionProvider::CreateFromString()` register built-ins once and delegate loading to `LoadSharedObject`.

## Control flow

File wrapper reads add `prefixLength_` to the caller offset before reading encrypted bytes, then decrypt the returned buffer in place. Sequential reads track `offset_`; `Skip()` advances the logical stream position; positioned sequential reads and random access reads translate offsets independently. Writes clone caller data into an `AlignedBuffer`, encrypt the clone at the physical offset, and pass only encrypted data to the wrapped file. The caller's input buffer is not mutated. Size, cache invalidation, allocation, truncation, range sync, and preallocation calls are translated by adding or subtracting the prefix length where they refer to file positions or lengths visible to RocksDB.

`EncryptedFileSystemImpl` handles construction paths separately for write, reopen, random read, sequential read, and random read/write. New writable files create a fresh prefix with `EncryptionProvider::CreateNewPrefix()`, write it to offset zero, then construct a stream from that prefix. Reads read the existing prefix before constructing a stream. Reopening a writable file reads an existing prefix for non-empty files and creates a fresh prefix for empty files. Random-RW files decide between read-prefix and write-prefix paths based on `FileExists()` before opening.

`BlockAccessCipherStream` computes `blockIndex = fileOffset / BlockSize()` and `blockOffset = fileOffset % BlockSize()`, then repeatedly encrypts or decrypts one block at a time. Partial-block ranges are copied into an uninitialized full-block buffer at the correct offset, transformed as a whole block, then copied back for only the requested range.

The CTR provider's prefix stores the initial counter in the first cipher block and the IV in the second cipher block. The remainder of the 4096-byte prefix is provider-specific secret prefix space and is encrypted using a CTR stream derived from the plaintext counter/IV. Opening an existing file decodes the counter/IV, checks that the prefix is at least two cipher blocks, decrypts the encrypted prefix tail, and creates a `CTRCipherStream` for file contents.

## State and persistence behavior

The persistent on-disk layout is `[encryption prefix][encrypted user data]`. `CTREncryptionProvider::defaultPrefixLength` is 4096 bytes to keep the first real data byte page-aligned for direct I/O. Public file sizes exclude this prefix; underlying file sizes include it. Prefix bytes are generated with `Random` seeded from `SystemClock::Default()->NowMicros()`, contain a random counter and IV, and may include encrypted subclass-specific prefix data via `PopulateSecretPrefixPart()`. The prefix is written once when a file is created or an empty file is reopened for writing.

The wrappers are largely stateless beyond the wrapped file pointer, the cipher stream, and prefix length. Sequential file wrappers also maintain the current physical offset. No key material is persisted directly by this file except for provider-defined prefix data; the actual cipher/key lifecycle is delegated to `EncryptionProvider` and `BlockCipher` implementations.

## Dependencies and integration points

This file depends on RocksDB's `FileSystem`/`Env` abstraction, `CompositeEnvWrapper`, `AlignedBuffer`, option registration (`OptionTypeInfo`, `RegisterOptions`), object registry loading (`LoadSharedObject`, `ObjectLibrary`), performance timers (`encrypt_data_nanos`, `decrypt_data_nanos`), and conversion between `Status` and `IOStatus`. It integrates with `file_system.cc` because `EncryptedFileSystem::kClassName()` is registered as a built-in file system there and constructed with `NewEncryptedFileSystemImpl()`. It also integrates with `env_test.cc` factory tests for `CTR`, `ROT13`, and `EncryptedFileSystem` option strings.

## Risks and edge cases

- `CreateSequentialCipherStream()` and `CreateRandomReadCipherStream()` use `provider_` directly rather than `GetReadableProvider()`, so a missing provider would be a crash risk if an improperly prepared `EncryptedFileSystemImpl` were used. Factory tests assert that provider-less encrypted FS configuration fails validation.
- `GetChildrenFileAttributes()` subtracts the provider prefix from every child returned by the underlying FS, but comments note directories are not distinguished. This can underflow or misreport directory sizes if directories are present and smaller than the prefix.
- `EncryptedWritableFile::GetFileSize()` subtracts `prefixLength_` from the underlying size without an explicit runtime guard. Correct construction requires the prefix to have been written first.
- Partial-block encryption/decryption transforms an uninitialized temporary full block except for the requested byte range. CTR mode makes this acceptable because only copied-back bytes matter, but non-CTR `BlockAccessCipherStream` subclasses must tolerate arbitrary bytes in the unrequested part of a partial block.
- CTR security depends entirely on the supplied `BlockCipher` and unique counter/IV per file. `ROT13BlockCipher` is test-only and unsafe.
- mmap reads/writes are rejected for encrypted files because the wrapper must transform bytes in userspace.
- Random-RW `isNewFile` is based on `FileExists()` before opening; unusual file-system races could choose the wrong prefix path.

## Test signals

`env_test.cc` covers the factory and configuration side: `LoadCTRProvider` exercises no-cipher failure, `CTR://test`, `1://test`, and `id=CTR; cipher=ROT13`; `LoadROT13Cipher` checks cipher factory loading; `CreateEncryptedFileSystem` checks the provider requirement, serialization/equivalence, default target wrapping, and wrapping over `TimedFileSystem`. Generic environment/file tests also indirectly exercise wrapper contracts such as size reporting, direct I/O option handling, file-system composition, and `SyncFile` behavior.
