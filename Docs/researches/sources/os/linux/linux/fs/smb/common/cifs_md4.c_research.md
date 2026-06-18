# File Research: sources/os/linux/linux/fs/smb/common/cifs_md4.c

## Scope
Read completely: 198 lines. This file implements an MD4 digest helper exported for CIFS/SMB code.

## Purpose
`cifs_md4.c` provides an in-tree MD4 implementation derived from historical CIFS and cryptoapi code. MD4 is needed for legacy NTLM-style password/hash operations in SMB authentication compatibility paths.

## Main Interfaces
- `int cifs_md4_init(struct md4_ctx *mctx)`
- `int cifs_md4_update(struct md4_ctx *mctx, const u8 *data, unsigned int len)`
- `int cifs_md4_final(struct md4_ctx *mctx, u8 *out)`

All three are exported with `EXPORT_SYMBOL_GPL`.

## Algorithm Structure
- Defines RFC1320 boolean functions `F`, `G`, and `H`.
- Defines rotate helper `lshift()`.
- Defines `ROUND1`, `ROUND2`, and `ROUND3` macros with MD4 constants.
- `md4_transform()` applies the three MD4 rounds to a 16-word block and accumulates state.
- `md4_transform_helper()` converts the current block from little-endian words to CPU order before transforming.

## State Handling
`struct md4_ctx` contains:
- four hash words.
- a 16-word block buffer.
- a byte counter.

`cifs_md4_init()` zeroes the context and sets the standard MD4 initial state:
- `0x67452301`
- `0xefcdab89`
- `0x98badcfe`
- `0x10325476`

`cifs_md4_update()`:
- Appends data into the partial block.
- Transforms complete 64-byte blocks.
- Leaves remaining bytes in `ctx->block`.
- Advances `byte_count`.

`cifs_md4_final()`:
- Adds `0x80` padding.
- Pads to the MD4 length field position.
- Writes bit length into block words 14 and 15.
- Performs the final transform.
- Converts hash words to little endian.
- Copies the 16-byte digest to `out`.
- Clears the context.

## Integration Points
The file includes `md4.h` and is built by `fs/smb/common/Makefile` under `CONFIG_SMBFS`. Consumers use it through `md4.h`.

## Security Notes
- MD4 is cryptographically broken and should only be used for legacy SMB/NTLM compatibility, not new security designs.
- The context is cleared in finalization, which is appropriate for password-derived hash material.

## Risks And Review Focus
- Length handling uses a 64-bit byte count but writes low/high bit length into 32-bit block words; this matches MD4 but depends on correct shifts.
- Endianness conversions are central to digest correctness.
- This implementation should not be generalized for non-legacy uses.

## Research Takeaways
`cifs_md4.c` is a small compatibility crypto primitive. Its main value is preserving legacy SMB authentication behavior while keeping the API local to SMB common code.
