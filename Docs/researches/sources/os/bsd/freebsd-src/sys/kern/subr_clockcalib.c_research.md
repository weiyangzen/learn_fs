# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_clockcalib.c

## Purpose
Calibrates an arbitrary hardware clock function against the current best timecounter using online statistical regression.

## Main Elements
- `clockcalib()`: samples the target clock and reference timecounter, computes running means, variances, and covariance, and returns the inferred target frequency.
- Handles wrapping of the reference timecounter by tracking an accumulated adjustment.
- Uses a 1 PPM uncertainty target and only accepts calibration after the uncertainty condition remains true for more than half the collected samples.
- Falls back to a slower direct ratio estimate if calibration takes more than one reference-clock second.
- Adds a decreasing variable spin delay to reduce aliasing risk between the sampling loop and reference clock.

## Dependencies And Integration
Uses the global `timecounter`, `tc_get_timecount()`, `tc_counter_mask`, `tc_frequency`, `cpu_spinwait()`, and TSLOG enter/exit instrumentation. Intended for early or low-level clock frequency calibration.

## Risk Notes
The method assumes both clocks tick at stable rates during sampling. If they vary, the function prints a warning and falls back. The implementation intentionally uses floating-point statistical calculations in kernel code, so architecture/kernel FP constraints matter for integration.
