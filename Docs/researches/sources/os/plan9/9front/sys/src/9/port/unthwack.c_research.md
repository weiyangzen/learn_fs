# File Research: sources/os/plan9/9front/sys/src/9/port/unthwack.c

Thwack decoder and decoder-history state management.

Key responsibilities:
- Initializes decoder block windows.
- Reports decoder state as newest sequence plus bitmask of nearby prior blocks.
- Inserts decoded blocks into the decoder window in sequence order, replacing the oldest slot.
- Reconstructs the encoder history set from packet sequence delta and mask bytes.
- Decodes adaptive literal encodings and variable-length match lengths.
- Decodes match offsets, finds the referenced block/data position, and copies match bytes into the current output block.
- Copies decoded output to the caller buffer and stores the block in decoder history.

Dependencies:
- Uses structures, constants, and sequence-window rules from `thwack.h`.

Notable behavior:
- Returns `-2` when required history blocks are missing and logs dropped-block information.
- Rejects malformed streams with invalid lengths, offsets beyond available history, output overflow, or insufficient bits.
- The decoder preserves separate compressed-block history from the caller-visible output buffer.
