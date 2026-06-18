# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/lpc.h

## Role

`private/lpc.h` declares linear predictive coding support for FLAC encoding and decoding: windowing, autocorrelation, LPC coefficient calculation, quantization, residual generation, residual bit-depth estimation, restore, expected coding cost, and best-order selection.

## API Surface

Non-integer-only builds expose windowed-data routines for 32-bit and 64-bit samples, autocorrelation, LPC coefficient generation, coefficient quantization, residual computation, limit-residual checks, expected bits-per-residual-sample, and best-order choice.

All builds expose max prediction/residual bit-depth helpers and LPC restore functions. Numerous conditional declarations expose SSE2, SSE4.1, AVX2, FMA, Power VSX, ARM64 NEON, and IA32 assembly variants.

## Important Contracts

Residual computation uses `data[-order, data_len-1]`, and restore requires historical samples in `data[-order,-1]`. `order` must be greater than zero for LPC paths and no more than `FLAC__MAX_LPC_ORDER`.

Quantization returns status codes: success, shift too large for header representation, or all-zero coefficients. Comments document that negative shifts may occur conceptually even though FLAC decoder-side shift representation is constrained.

## Risks / Edge Cases

- Callers must pass valid history before the current data pointer.
- Assembly/intrinsic declarations are tightly coupled to build macros and CPU feature detection.
- Residual limit variants are important for rejecting values not representable as legal 32-bit FLAC residuals.
- Floating LPC analysis is excluded under integer-only builds, but restore/bit-depth helpers remain.

## Dependencies

Includes `private/cpu.h`, `private/float.h`, and `FLAC/format.h`.
