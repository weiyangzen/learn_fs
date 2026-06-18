# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdct.h

Purpose: private shared declarations for forward and inverse DCT modules.

Key definitions:
- `DCTELEM` is `int` for 8-bit samples and `INT32` for wider sample builds.
- Function pointer types: `forward_DCT_method_ptr`, `float_DCT_method_ptr`.
- IDCT multiplier table element types: `ISLOW_MULT_TYPE`, `IFAST_MULT_TYPE`, `FLOAT_MULT_TYPE`.
- `IDCT_range_limit(cinfo)` and `RANGE_MASK` define the bulletproof post-IDCT range-limiting convention.
- External declarations for forward DCTs: `jpeg_fdct_islow`, `jpeg_fdct_ifast`, `jpeg_fdct_float`.
- External declarations for inverse DCTs: `jpeg_idct_islow`, `jpeg_idct_ifast`, `jpeg_idct_float`, reduced-size IDCTs `4x4`, `2x2`, `1x1`.
- Fixed-point arithmetic helpers: `ONE`, `CONST_SCALE`, `FIX`, `DESCALE`, `MULTIPLY16C16`, `MULTIPLY16V16`.

Important behavior:
- Documents the convention that forward DCT output is scaled up by 8.
- IDCT routines are expected to perform dequantization and range limiting themselves.
- Supports old toolchains with optional short external names and multiply-cast tuning macros.

Dependencies:
- Consumed by DCT manager and individual DCT/IDCT implementations.
- Depends on JPEG scalar types, `DCTSIZE`, `DCTSIZE2`, `BITS_IN_JSAMPLE`, and right-shift macros from the JPEG portability layer.

Notes:
- This header is central to the decoder/encoder DCT ABI inside the vendored IJG code.
