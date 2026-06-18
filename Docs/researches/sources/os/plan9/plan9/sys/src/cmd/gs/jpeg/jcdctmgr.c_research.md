# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcdctmgr.c

Forward-DCT manager for JPEG compression.

Key behavior:
- Selects the configured FDCT implementation: slow integer, fast integer, or floating point when compiled in.
- Verifies each component's referenced quantization table exists before a pass.
- Builds per-quant-table divisor arrays adjusted for DCT scaling, including AA&N scale factors for fast integer/float DCTs.
- Converts unsigned samples to centered DCT input, calls the selected FDCT routine, then quantizes coefficients into JPEG coefficient blocks.
- Uses a fast zero-result path for division unless `FAST_DIVIDE` is defined.

Dependencies:
- Depends on `jdct.h` FDCT implementations (`jpeg_fdct_islow`, `jpeg_fdct_ifast`, `jpeg_fdct_float`) and IJG quantization/component state.
- Uses image-pool allocations for divisor tables.

Notable risks:
- The selected `dct_method` must match compile-time feature macros or initialization errors with `JERR_NOT_COMPILED`.
- Quantization table presence is enforced at pass start, not when parameters are initially set.
- The integer path has careful sign handling because C division rounding for negatives is not portable.
