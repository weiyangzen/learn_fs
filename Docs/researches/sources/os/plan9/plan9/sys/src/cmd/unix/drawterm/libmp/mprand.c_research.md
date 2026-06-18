# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mprand.c

Creates random multiprecision integers.

Key function:
- `mprand`: fills random bytes using caller-supplied generator, converts via `betomp`, masks excess high bits, normalizes top, and sets positive sign.

Important behavior:
- The generator callback has signature `void (*gen)(uchar*, int)`.
- Allocates a byte buffer sized to the digit count for the requested bit length.
