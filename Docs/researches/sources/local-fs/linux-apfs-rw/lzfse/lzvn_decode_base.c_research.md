# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzvn_decode_base.c

## Purpose
Implements the low-level LZVN decoder used for LZFSE streams that contain LZVN-compressed blocks.

## Main Responsibilities
- Dispatches all 256 opcode values through a computed-goto jump table.
- Handles opcodes for small/medium/large distance literal+match pairs, previous-distance matches, literal-only runs, match-only runs, NOP, EOS, and undefined opcodes.
- Copies literals from source and matches from previously emitted destination bytes.
- Preserves partial literal/match state when the destination buffer fills.
- Maintains previous match distance for opcodes that reuse it.

## Key Function
- `lzvn_decode(lzvn_decoder_state *state)`: updates source pointer, destination pointer, previous distance, partial L/M/D state, and EOS status in place.

## Dependencies
Includes `lzvn_decode_base.h`, Linux compiler/version headers, and utility functions from `lzfse_internal.h`.

## Notes
The decoder uses wide 4-byte and 8-byte copies on fast paths but falls back to byte-wise copies near buffer ends or for overlapping short-distance matches. Invalid match distances and undefined opcodes stop decoding after state has been updated to the last good instruction boundary.
