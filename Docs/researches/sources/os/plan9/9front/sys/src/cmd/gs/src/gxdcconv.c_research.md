# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcconv.c

Device color-space conversion helpers.

Key behavior:
- Converts RGB fractions to gray using luminance weights.
- Converts RGB to CMYK, including black generation and undercolor removal from the imager state when available.
- Converts CMYK to gray through luminance of CMY plus black.
- Converts CMYK to RGB, using Adobe-compatible formulas when `USE_ADOBE_CMYK_RGB` is defined.
- Emits color-conversion debug traces under the `c` debug flag.

Notable dependencies:
- Fraction arithmetic, luminance weights, imager-state transfer maps, and color-map helpers.

Research notes:
- Gray-to-RGB and gray-to-CMYK are treated as trivial and implemented elsewhere.
- The file supports both Adobe-style CMYK/RGB conversion and an alternate multiplicative model behind preprocessor conditionals, but this build selects Adobe behavior.
- Passing a null imager state changes RGB-to-CMYK behavior to use default identity-like assumptions.
