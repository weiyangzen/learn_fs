# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpaux.c

Core allocation and utility support for libmp.

Key globals:
- Static constants `mpzero`, `mpone`, and `mptwo`.
- `mpmindigits`: minimum allocation size.

Key functions:
- `mpsetminbits`, `mpnew`, `mpbits`, `mpfree`.
- `mpnorm`, `mpcopy`, `mpassign`.
- `mpsignif`: significant bit count.
- `mplowbits0`: count trailing zero bits.

Important behavior:
- `mpfree` zeroes limb data before freeing and refuses to free static constants.
- `mpbits` expands storage and zero-fills new limbs.
