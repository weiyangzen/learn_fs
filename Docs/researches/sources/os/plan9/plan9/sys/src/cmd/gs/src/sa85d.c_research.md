# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sa85d.c

Implementation of Ghostscript’s `ASCII85Decode` stream filter.

Core behavior:

- Defines `s_A85D_init`, which delegates to the inline initializer from `sa85d.h`.
- Implements `s_A85D_process`, reading ASCII85 input digits and writing decoded binary bytes.
- Handles ordinary base-85 groups, the `z` shorthand for four zero bytes, whitespace via `scan_char_decoder`, and end marker `~>`.
- Allows CR/LF between `~` and `>` for Adobe Acrobat compatibility, while treating other intervening characters as errors.
- Checks for 32-bit overflow in final group assembly.
- Supports partial final groups through `a85d_finish`.
- Emits stream statuses `0`, `1`, `EOFC`, or `ERRC` using Ghostscript stream conventions.
- Exposes `s_A85D_template` with min input/output sizes `2` and `4`.

This is byte-stream decoding code. It has no filesystem behavior.
