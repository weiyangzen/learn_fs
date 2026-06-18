# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/fixed.h

## Role

`private/fixed.h` declares fixed-predictor analysis, residual generation, and signal restoration routines for FLAC fixed subframes.

## API Surface

The best-predictor functions estimate residual bits per sample for orders 0 through `FLAC__MAX_FIXED_ORDER`, with normal, wide, limit-residual, and 33-bit variants. Non-integer-only builds return floating estimates; integer-only builds use `FLAC__fixedpoint`.

Residual functions compute fixed-predictor residuals from original samples. Restore functions reconstruct samples from residuals and historical samples. Optional SSE2, SSSE3, and NASM IA32 declarations expose optimized predictor selection variants.

## Important Contracts

Residual computation takes `data[-order, data_len-1]`; restoration requires `data[-order,-1]` historical samples already available before the output pointer. This negative-index convention is central to FLAC fixed predictor code.

## Risks / Edge Cases

- Callers must pass sufficient warm-up/history samples before the data pointer.
- Wide and 33-bit variants are required when sample depth plus blocksize can overflow narrower accumulators.
- Assembly/intrinsic declarations are conditional on CPU/build macros and must match compiled implementation availability.

## Dependencies

Includes `private/cpu.h`, `private/float.h`, and `FLAC/format.h`.
