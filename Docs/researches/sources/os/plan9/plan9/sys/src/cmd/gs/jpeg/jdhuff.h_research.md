# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdhuff.h

Purpose: private shared declarations and hot-path macros for sequential and progressive Huffman decoders.

Key definitions:
- `HUFF_LOOKAHEAD = 8`.
- `d_derived_tbl` stores `maxcode`, `valoffset`, public table backlink, and lookahead decode tables.
- `bit_buf_type`, `BIT_BUF_SIZE`, `bitread_perm_state`, and `bitread_working_state` define entropy bit-buffer state.
- `BITREAD_STATE_VARS`, `BITREAD_LOAD_STATE`, and `BITREAD_SAVE_STATE` manage suspension-safe local/permanent state transfer.
- `CHECK_BIT_BUFFER`, `GET_BITS`, `PEEK_BITS`, `DROP_BITS` implement inline bit access.
- `HUFF_DECODE` implements the fast lookahead path with fallback to `jpeg_huff_decode()`.

Important behavior:
- The macros assume `get_buffer` and `bits_left` are local variables, which is why decode functions have a specific shape.
- `jpeg_fill_bit_buffer()` may return false for source suspension; callers provide an action.
- `HUFF_DECODE` returns symbols directly for common short codes and jumps to a caller-provided slow label otherwise.

Dependencies:
- Implementations live in `jdhuff.c`; progressive decoder reuses them.
- Depends on source-manager buffer state and JPEG scalar types.

Notes:
- This header is performance-critical and intentionally macro-heavy.
