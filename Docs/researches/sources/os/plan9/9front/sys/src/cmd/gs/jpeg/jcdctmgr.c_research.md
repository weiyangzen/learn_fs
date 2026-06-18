# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcdctmgr.c

Forward DCT manager and coefficient quantizer for compression.

Key points:
- Selects the active DCT implementation (`JDCT_ISLOW`, `JDCT_IFAST`, or `JDCT_FLOAT`) based on compile-time support and `cinfo->dct_method`.
- `start_pass_fdctmgr` verifies each component’s quantization table and builds scaled divisor tables for the chosen DCT method.
- Integer DCT path copies input samples into a centered workspace, runs the selected integer FDCT, then quantizes each coefficient with portable rounding for negative values.
- Floating DCT path uses reciprocal floating divisors and rounds via a bias technique.
- Initializes divisor arrays lazily per quant table and marks unused slots `NULL`.

Dependencies and interactions:
- Includes `jdct.h` for private DCT routine declarations.
- Called by the coefficient controller for block-row FDCT/quantization.
- Depends on quant tables prepared by `jcparam.c` or application-supplied table setup.

Risk notes:
- If a requested DCT method was not compiled, initialization errors with `JERR_NOT_COMPILED`.
- Quantization table absence is detected at pass start, not when parameters are set.
- The integer path’s division macro can trade correctness-preserving speed behavior via `FAST_DIVIDE`.
