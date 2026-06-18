# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpvecsub.c

Implements `mpvecsub(mpdigit *a, int alen, mpdigit *b, int blen, mpdigit *diff)`, subtracting limb vector `b` from `a`. The documented preconditions are `a >= b`, `alen >= blen`, and `diff` has at least `alen` digits.

The overlapping range subtracts each `b` limb and incoming borrow from `a`, using unsigned comparisons to detect borrow propagation. Remaining high limbs of `a` are copied through with borrow subtraction.

This is magnitude-only, low-level arithmetic. It assumes the caller has already compared magnitudes and arranged sign/result normalization at the `mpint` layer.
