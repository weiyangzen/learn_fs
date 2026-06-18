# File Research: sources/local-fs/apfs-fuse/Crypto/Sha1.h

## Role

`Sha1.h` declares the local SHA-1 streaming hash class.

## Public Interface

- `Init()` resets hash state.
- `Update(data, size)` absorbs bytes.
- `Final(hash)` writes a 20-byte digest.

## Internal State

- `m_buffer[64]` stores partial blocks.
- `m_hash[5]` stores the current SHA-1 chaining state.
- `m_bit_cnt` stores total input bits.
- `m_buf_idx` stores partial-buffer position.
- `m_K[4]` stores SHA-1 round constants.

## Notable Limitations And Risk Areas

- Digest output length is implicit; callers must provide at least 20 bytes.
- The class is mutable and not thread-safe if shared.
