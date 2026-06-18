# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileEncrypted.h

## Purpose
`AsyncFileEncrypted.h` declares an `IAsyncFile` wrapper for AES-256-GCM encrypted append-only files with read-only and append-only modes.

## Important APIs, Types, and Functions
`AsyncFileEncrypted` exposes `Mode { APPEND_ONLY, READ_ONLY }`, constructor `AsyncFileEncrypted(Reference<IAsyncFile>, Mode, int)`, reference counting overrides, `read`, `write`, `zeroRange`, `truncate`, `sync`, `flush`, `size`, `getFilename`, zero-copy methods, and `debugFD`. Private helpers include `getIV`, `writeLastBlockToFile`, and `initialize`.

## Control Flow
The header declares the control surface; implementation elsewhere initializes encryption state, derives IVs per block, buffers append data, writes encrypted blocks, and decrypts reads. Append-only mode maintains current block and offset; read-only mode serves decrypted reads over the wrapped file.

## State and Persistence Behavior
Durable bytes are stored encrypted in the wrapped file. In-memory state includes the first block IV, mode, cached file size, encryption stream cipher, current block number, offset within the encryption block, write buffer, and encryption block size.

## Dependencies and Integration Points
It depends on `flow/IAsyncFile.h`, Flow reference counting, deterministic random support, and `flow/StreamCipher.h`. It integrates with any FoundationDB code that can consume an `IAsyncFile` while requiring encryption at rest.

## Risks and Edge Cases
Append-only semantics mean random writes, truncation, and zeroing need strict mode enforcement. IV derivation and block-boundary handling are security-critical. The header exposes zero-copy methods but encrypted data generally cannot be returned as stable raw underlying buffers without decryption ownership handling.

## Test Signals
Relevant signals are encryption wrapper tests, round-trip read/write checks, append boundary tests, sync/flush behavior, and failure of unsupported mutation methods in read-only mode.
