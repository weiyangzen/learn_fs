# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inffast.c

## Purpose
Implements the optimized inner loop for inflate literal/length/distance decoding.

## Key Elements
Exports `inflate_fast(z_streamp strm, unsigned start)` unless `ASMINF` supplies an assembler implementation. It caches stream pointers, bit buffer, window state, and decode tables in locals, then decodes literals and match copies until input/output space is no longer sufficient, an end-of-block is reached, or an error occurs.

## Behavior/Risks
Entry assumes `state->mode == LEN`, at least six bytes of input, at least 258 bytes output space, and `state->bits < 8`. It handles two-level Huffman decode table entries, copies matches either from current output or the sliding window, and reports invalid distance/literal codes through `state->mode = BAD` and `strm->msg`. Correctness relies on callers enforcing the buffer-size assumptions.

## Dependencies
Includes `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. Used by both `inflate.c` and `infback.c`.
