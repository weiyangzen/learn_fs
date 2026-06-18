# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/stream_encoder.h

## Role

`private/stream_encoder.h` declares internal encoder support constants and SIMD entry points for residual partition precomputation.

## Contents

It defines `FLAC__MAX_EXTRA_RESIDUAL_BPS` as `4`, used to avoid overflow in unusual signals when precomputing partition sums with 32-bit accumulators.

For x86/x86_64 builds with intrinsics, it declares SSE2, SSSE3, and AVX2 versions of `FLAC__precompute_partition_info_sums_*()`.

## Risks / Edge Cases

The optimized declarations are gated by CPU and build macros. Encoder dispatch must only call implementations that were compiled and are supported on the runtime CPU.

## Dependencies

Conditionally includes `private/cpu.h` and `FLAC/format.h`.
