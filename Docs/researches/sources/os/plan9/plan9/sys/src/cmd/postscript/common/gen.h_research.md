# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/gen.h

General constants and macros for the PostScript translator suite.

Key responsibilities:
- Defines program version, fatality constants, boolean constants, byte masks, points-per-inch, pi, encoding modes, page defaults, and simple `ABS/MIN/MAX` macros.
- Enables `DOROUND` by default for translators that include page-rounding prologue code.
- Sets default page dimensions used in bounding-box calculations.

Notable risks:
- Macro names such as `FATAL`, `TRUE`, and `FALSE` overlap with other headers.
