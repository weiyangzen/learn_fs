# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/fixed.c

## Purpose

This file implements fixed-order linear prediction helpers for FLAC orders 0 through 4. It chooses the best fixed predictor, estimates residual bits per sample, computes residual signals, and restores decoded signals from residuals. It has normal 32-bit, wider arithmetic, and 33-bit data variants.

## Predictor Selection

`FLAC__fixed_compute_best_predictor()` computes absolute residual totals for orders 0 to 4 using first through fourth finite differences, chooses the order with the smallest total error while preferring lower order on ties, and estimates residual bits per sample.

`FLAC__fixed_compute_best_predictor_wide()` performs the same work with 64-bit error totals to avoid overflow for large blocks or erratic signals.

`FLAC__fixed_compute_best_predictor_limit_residual()` and `_33bit()` additionally track whether each order can produce residuals that fit within signed 32-bit limits. Invalid orders receive a high placeholder residual-bit estimate and are excluded from selection.

## Residual Bit Estimates

For normal builds, residual-bit estimates use `log(M_LN2 * error / data_len) / M_LN2`. For `FLAC__INTEGER_ONLY_LIBRARY`, helper functions compute fixed-point approximations:

- `local__compute_rbps_integerized()` for 32-bit total error.
- `local__compute_rbps_wide_integerized()` for 64-bit total error.

Those helpers use integer log2 routines from `private/bitmath.h` and `FLAC__fixedpoint_log2()` from `float.c`.

## Residual and Restore Operations

- `FLAC__fixed_compute_residual()` writes residuals for orders 0 to 4 using 32-bit expressions.
- `FLAC__fixed_compute_residual_wide()` casts operands to 64-bit during calculation before storing int32 residuals.
- `FLAC__fixed_compute_residual_wide_33bit()` accepts int64 input data for special wider predictor paths.
- `FLAC__fixed_restore_signal()` reconstructs int32 signal data from residuals and warm-up samples.
- `FLAC__fixed_restore_signal_wide()` reconstructs int32 data using 64-bit intermediate arithmetic.
- `FLAC__fixed_restore_signal_wide_33bit()` reconstructs int64 data from int32 residuals.

## Integration Points

The file includes `private/fixed.h`, `private/bitmath.h`, `private/macros.h`, `share/compat.h`, and `FLAC/assert.h`. It is used by encoder analysis to select fixed subframes and by decoder paths to restore fixed-predictor subframes.

## Risks and Notes

Predictor/residual loops intentionally read `data[i - order]`, so callers must provide valid warm-up samples before the data pointer for orders greater than zero. The limit-residual variants protect against `INT32_MIN` absolute-value undefined behavior by marking orders invalid when residual magnitudes exceed `INT32_MAX`. There are explicit "kencc workaround" comments in 33-bit order-4 paths, splitting arithmetic into multiple statements to avoid register pressure in the Plan 9 C compiler.
