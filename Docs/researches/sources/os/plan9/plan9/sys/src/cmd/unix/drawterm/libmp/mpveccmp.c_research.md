# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpveccmp.c

Implements `mpveccmp(mpdigit *a, int alen, mpdigit *b, int blen)`, comparing two little-endian limb vectors as unsigned magnitudes.

It first trims effective high zero limbs from the longer vector, then walks equal-length vectors from high limb to low limb. The subtraction/wraparound test distinguishes `a[alen] < b[alen]` without requiring a wider type.

Return values follow normal compare semantics: `1` if `a > b`, `-1` if `a < b`, and `0` if magnitudes match. No allocation, normalization, or sign handling occurs here.
