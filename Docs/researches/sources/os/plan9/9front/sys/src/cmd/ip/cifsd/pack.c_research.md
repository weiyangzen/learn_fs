# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/pack.c

Implements a compact binary format language for SMB message packing and unpacking.

Key points:
- Public wrappers `pack`/`unpack` call `vpack`/`vunpack`.
- Supports format operators:
  - `_` skip/zero byte
  - `b`, `w`, `l`, `v` for little-endian 8/16/32/64-bit values
  - `%n` alignment
  - `f` custom pack/unpack function
  - `#` count field and `@` offset field tied to sub-block index
  - `{}` sub-blocks with counted/offset-delimited regions
  - `[]` copy/expose raw byte ranges
  - `.` capture current pointer
- `vunpack` tracks nested sub-blocks, applies counts/offsets, bounds checks, and returns bytes consumed.
- `vpack` mirrors the same mechanism, backpatching count and offset fields when sub-blocks close.
- Fixed-size sub-block item width can be specified with `{*n}`/`[*n]`.
- Returns 0 on malformed/truncated/bounds-failing input.

Dependencies and interactions:
- Used heavily by SMB request parsing, response construction, transaction/RAP responses, and string/name packers.

Research relevance:
- This is the low-level serialization engine for CIFS protocol handling.
