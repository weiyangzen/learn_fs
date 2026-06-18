# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inffast.c

## Purpose
Implements `inflate_fast()`, the optimized inner loop for deflate decoding. It handles the common hot path where enough input and output space are available to decode without frequent boundary checks.

## Entry Conditions
The caller must ensure:
- `state->mode == LEN`.
- `strm->avail_in >= 6`.
- `strm->avail_out >= 258`.
- `start >= strm->avail_out`.
- `state->bits < 8`.

These constraints let the loop decode the maximum possible length/distance pair without checking for more input or output on every step.

## Core Behavior
The routine copies stream and inflate-state fields into local variables, decodes literal/length codes and distance codes from the current Huffman tables, and writes output bytes. It handles:
- Literals.
- Length/distance matches copied from current output.
- Matches copied from the sliding window, including wraparound.
- Second-level Huffman decode table entries.
- End-of-block and invalid-code transitions.

On return, it updates `next_in`, `next_out`, `avail_in`, `avail_out`, `state->hold`, and `state->bits`.

## Portability/Optimization
`POSTINC` controls whether pointer increments are pre- or post-increment, based on historical CPU performance testing. `ASMINF` can disable the C implementation for assembly replacements.

## Error Handling
Invalid distance or literal/length codes set `strm->msg` and move `state->mode` to `BAD`; end-of-block moves to `TYPE`; otherwise the function returns with `LEN` when input/output thresholds are no longer met.
