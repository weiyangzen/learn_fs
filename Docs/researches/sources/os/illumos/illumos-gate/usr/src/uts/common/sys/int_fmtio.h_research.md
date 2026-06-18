# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_fmtio.h

This header implements ISO C99 `<inttypes.h>` printf/scanf format macros for fixed-width integer types, plus illumos non-standard extensions.

Key definitions:
- Print macros for signed and unsigned fixed-width, least, fast, pointer, and max integer types: `PRId*`, `PRIi*`, `PRIo*`, `PRIu*`, `PRIx*`, `PRIX*`.
- Scan macros: `SCNd*`, `SCNi*`, `SCNo*`, `SCNu*`, `SCNx*`, `SCNX*`.
- Pointer formats switch between `l` forms on `_LP64` and plain int forms on ILP32.
- `PRIdMAX`/friends and `SCNdMAX`/friends use `ll` on ILP32 with long long and `l` otherwise.

Kernel/user note:
- `_MODF8` and `_MODF16` suppress `hh`/`h` in `_KERNEL`, while userland gets standard small-width modifiers.

Non-standard extensions:
- Under non-strict symbols, defines private `_PRI*ID`/`_SCN*ID` formats for `id_t`.
- Defines `_PRI*WC`/`_SCN*WC` aliases for `wint_t`/`wchar_t`-like formatting.

Dependencies:
- Includes `sys/feature_tests.h`.

Relevance:
- Widespread diagnostic and ABI formatting support; important for correct cross-data-model logging and parsing.
