# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpvecadd.c

Implements low-level limb-vector addition `mpvecadd(mpdigit *a, int alen, mpdigit *b, int blen, mpdigit *sum)`. The documented precondition is `alen >= blen`, and `sum` must have room for `alen + 1` digits.

The routine first adds overlapping limbs from `a` and `b` with carry detection based on unsigned wraparound, then propagates carry across the remaining high limbs of `a`. It stores a final carry digit at `sum[alen]`.

This is magnitude-only arithmetic used by higher-level `mpint` operations. It does not normalize or allocate; callers are responsible for sizes, aliasing safety, and sign semantics.
