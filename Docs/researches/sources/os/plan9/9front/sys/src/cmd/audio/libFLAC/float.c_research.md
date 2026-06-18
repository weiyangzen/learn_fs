# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/float.c

## Purpose

This file provides fixed-point constants and a fixed-point base-2 logarithm implementation for integer-only libFLAC builds. In non-integer-only builds, the file contributes no active functions beyond includes and conditional compilation.

## Integer-Only Contents

When `FLAC__INTEGER_ONLY_LIBRARY` is defined, the file exports fixed-point constants:

- `FLAC__FP_ZERO`
- `FLAC__FP_ONE_HALF`
- `FLAC__FP_ONE`
- `FLAC__FP_LN2`
- `FLAC__FP_E`

It also defines `log2_lookup`, a table of precomputed logarithm increments for fractional precisions from 0 to 28 bits in steps of 4. A disabled wide lookup table documents possible 32-bit and 48-bit fractional precision constants.

## Main Function

`FLAC__fixedpoint_log2(FLAC__uint32 x, uint32_t fracbits, uint32_t precision)` computes a fixed-point base-2 logarithm using Knuth's algorithm and the lookup table selected by `fracbits >> 2`.

The function asserts `fracbits < 32` and that `fracbits` is divisible by 4. Inputs smaller than one fixed-point unit return zero. Requested precision is capped at the lookup-table width. The loop subtracts progressively halved terms and accumulates table entries until the desired precision is reached.

## Integration Points

The file includes `private/float.h`, `FLAC/assert.h`, and `share/compat.h`. `fixed.c` uses this function for residual bits-per-sample estimation in integer-only builds.

## Risks and Notes

The implementation assumes callers provide a fractional-bit count supported by the lookup table. It trades precision for small tables and deterministic integer arithmetic, which is useful on platforms or builds avoiding floating-point math.
