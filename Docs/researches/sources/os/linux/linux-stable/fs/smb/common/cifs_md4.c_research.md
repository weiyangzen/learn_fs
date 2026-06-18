# File Research: sources/os/linux/linux-stable/fs/smb/common/cifs_md4.c

## Summary
Implements MD4 hashing for CIFS/SMB common code. It is derived from older CIFS and Linux crypto API MD4 implementations and exports a small init/update/final interface.

## Main Interfaces
- `cifs_md4_init(struct md4_ctx *mctx)`: zeroes context and initializes MD4 IV words.
- `cifs_md4_update(struct md4_ctx *mctx, const u8 *data, unsigned int len)`: buffers input, transforms full 64-byte blocks, and tracks byte count.
- `cifs_md4_final(struct md4_ctx *mctx, u8 *out)`: appends MD4 padding and bit length, performs final transform, writes the little-endian digest, and clears context.

## Internal Logic
The file defines MD4 primitives `F`, `G`, `H`, rotate helper `lshift()`, round macros, `md4_transform()`, and `md4_transform_helper()` for little-endian block conversion. The transform performs the three MD4 rounds over 16 32-bit words and accumulates into the hash state.

## Integration Notes
The symbols are exported with `EXPORT_SYMBOL_GPL`, and `md4.h` defines context sizes and prototypes. This implementation is likely used for legacy NTLM/CIFS authentication compatibility rather than general-purpose cryptographic strength.

## Risks
MD4 is cryptographically broken and should remain limited to protocol compatibility. Correctness-sensitive areas are byte-count overflow assumptions, final padding length, little-endian conversion, and context clearing after finalization.
