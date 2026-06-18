# sources/distributed-fs/tahoe-lafs/src/allmydata/util/mathutil.py

## Purpose

This module is a backwards-compatibility import surface for common math helpers from `pyutil.mathutil`, plus Tahoe's local `round_sigfigs()`. Many older modules import these helpers from `allmydata.util.mathutil`.

## APIs and control flow

It re-exports `div_ceil`, `next_multiple`, `pad_size`, `is_power_of_k`, `next_power_of_k`, `ave`, `log_ceil`, and `log_floor`. `round_sigfigs(f, n)` formats `f` in scientific notation with `n-1` fractional digits and converts back to float. `__all__` documents the public names.

## State, dependencies, risks, and tests

There is no state or persistence. Dependencies are only `pyutil.mathutil` and Python float formatting. Integration includes base62 length math and statistics output.

Risks include behavior drift in pyutil imports, floating-point rounding surprises in `round_sigfigs()`, and divide/log helper edge cases inherited from pyutil. Test signals should cover import compatibility, ceiling/floor logarithms used by base62, significant-figure formatting for small/large/negative values, and `__all__` correctness.
