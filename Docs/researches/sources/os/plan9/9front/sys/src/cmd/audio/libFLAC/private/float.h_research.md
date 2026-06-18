# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/float.h

## Role

`private/float.h` centralizes libFLAC's floating-point or fixed-point analysis type definitions.

## Contents

For normal builds, `FLAC__real` is typedefed to `float`. Comments warn that changing it affects many function signatures and assembly-equivalent routines.

For `FLAC__INTEGER_ONLY_LIBRARY`, it defines `FLAC__fixedpoint` as `FLAC__int32`, declares fixed-point constants, provides truncation/multiply/divide macros using 16 fractional bits, and declares `FLAC__fixedpoint_log2()`.

## Important Implementation Details

The fixed-point convention uses upper 16 bits as integer part and lower 16 bits as fractional part. `FLAC__fixedpoint_log2()` takes an input fixed-point value, caller-specified fractional bits, and precision control.

## Risks / Edge Cases

- Floating and integer-only builds expose different signatures in predictor headers.
- Fixed-point division can divide by zero if callers do not validate inputs.
- Changing `FLAC__real` would break ABI/assembly assumptions.

## Dependencies

Includes `config.h` when available and `FLAC/ordinals.h`.
