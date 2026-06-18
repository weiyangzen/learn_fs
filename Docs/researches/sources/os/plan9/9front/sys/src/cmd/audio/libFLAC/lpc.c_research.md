# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/lpc.c

## Role

`lpc.c` implements libFLAC linear predictive coding support for FLAC encoding and decoding. It covers windowing, autocorrelation, Levinson-Durbin LPC coefficient generation, QLP coefficient quantization, residual generation, signal restoration, residual bit-depth estimation, and best-order selection.

This is codec math code rather than filesystem code, but it is part of the 9front Plan 9 audio command source tree.

## Major Functions

- `FLAC__lpc_window_data*()` multiplies 32-bit or 64-bit sample input by a floating-point analysis window. Partial variants handle shifted partition windows.
- `FLAC__lpc_compute_autocorrelation()` computes autocorrelation for requested lags using a locality-oriented loop.
- `FLAC__lpc_compute_lp_coefficients()` derives LPC coefficients and error terms from autocorrelation, stopping early if prediction error reaches zero.
- `FLAC__lpc_quantize_coefficients()` scales floating-point LPC coefficients into signed integer QLP coefficients, with shift-limit handling and clipping.
- `FLAC__lpc_compute_residual_from_qlp_coefficients*()` computes encoded residuals from input samples and QLP predictors.
- `FLAC__lpc_compute_residual_from_qlp_coefficients_limit_residual*()` validates residuals fit in signed 32-bit range and are not `INT32_MIN`.
- `FLAC__lpc_restore_signal*()` reconstructs decoded samples from residuals and predictor history.
- `FLAC__lpc_max_prediction_before_shift_bps()` and `FLAC__lpc_max_residual_bps()` estimate predictor and residual bit widths.
- `FLAC__lpc_compute_expected_bits_per_residual_sample*()` and `FLAC__lpc_compute_best_order()` estimate coding cost and select the best LPC order.

## Plan 9 / Portability Notes

The file has a Plan 9-specific compatibility branch defining `_copysign()` and `lround()` when `Plan9` is defined. Floating-point LPC analysis is excluded under `FLAC__INTEGER_ONLY_LIBRARY`, but residual restore and bit-depth helpers remain available.

## Important Implementation Details

The hot residual and restore paths use hand-unrolled branches for LPC orders up to 12, then a fallthrough `switch` for orders up to 32. These functions intentionally index `data[i-order]` and similar negative offsets from the current data pointer; callers must pass a pointer positioned after warm-up samples.

There are normal and wide paths. Normal paths accumulate in `FLAC__int32`; wide paths use `FLAC__int64`. The limit-residual variants are safer for encoder decisions because they reject residuals outside the legal 32-bit range before storing.

Coefficient quantization can return `0` for success, `1` if a negative shift is too small to represent, and `2` if all coefficients are zero. A rare negative shift is handled by scaling coefficients down and then forcing shift to zero, because FLAC decoder-side LPC shifts cannot be negative.

## Risks / Edge Cases

- The performance paths rely heavily on signed integer overflow behavior in audio math. Fuzzing builds can suppress signed-overflow sanitizer for restore functions.
- The unrolled loops require `order > 0` and `order <= 32`; these are asserted, not fully runtime-validated in release builds.
- Residual and restore callers must preserve enough predictor history before the `data` pointer.
- `FLAC__lpc_max_prediction_before_shift_bps()` sums `abs(qlp_coeff[i])` into `FLAC__int32`; extremely large coefficient sets would be risky, though FLAC coefficient precision normally bounds this.

## Dependencies

Uses `FLAC/assert.h`, `FLAC/format.h`, `private/bitmath.h`, `private/lpc.h`, `private/macros.h`, and `share/compat.h`. The file depends on libFLAC numeric typedefs and format constants such as `FLAC__MAX_LPC_ORDER`.
