# File Research: sources/os/plan9/9front/sys/src/9/mt7688/fpimem.c

Memory-format conversion routines for the MT7688 floating-point interpreter. It converts between IEEE single/double/integer memory values and the internal `Internal` FP format.

Input conversions include single-to-internal, double-to-internal, 32-bit word-to-internal, and 64-bit integer-to-internal. Output conversions round the internal value and produce single, double, 32-bit integer, or 64-bit integer results, including underflow-to-zero and saturation-style max integer handling.

Notable risks: output conversions intentionally mutate the supplied `Internal`, so callers must pass disposable copies; integer negation of minimum negative values relies on C two's-complement behavior assumptions.
