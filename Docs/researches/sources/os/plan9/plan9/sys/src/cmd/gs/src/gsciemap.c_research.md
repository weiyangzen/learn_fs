# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsciemap.c

## Purpose
Hot-path CIE color rendering. It maps CIEBasedA/ABC/DEF/DEFG client colors through the sampled caches prepared by `gscie.c` into concrete RGB, CMYK, separation, or XYZ-like output.

## Key Behavior
- Converts CIEDEFG and CIEDEF inputs through DecodeDEF[G], table interpolation, RangeABC scaling, DecodeABC/MatrixABC, and final CIE remapping.
- Implements `gx_remap_CIEABC` for efficient rendering into a `gx_device_color`.
- Implements concretization for CIEABC and CIEA.
- `gx_cie_real_remap_finish` performs shared finishing stages:
  - DecodeLMN/MatrixLMN/MatrixPQR,
  - TransformPQR/MatrixPQR inverse/MatrixLMN,
  - EncodeLMN/MatrixABC,
  - EncodeABC,
  - optional RenderTable lookup and RenderTable.T mapping.
- Supports RenderTable interpolation when enabled.
- `gx_cie_xyz_remap_finish` returns the intermediate XYZ path for high-level devices.
- `cie_lookup_mult3` performs cache lookup with optional interpolation and cached matrix contribution addition.

## Important Details
- The `LOOKUP_INDEX` macros are kept macro-based in non-debug builds because this path is extremely time-sensitive.
- DEF/DEFG table inputs are interpolated manually from decoded cached values and then passed to `gx_color_interpolate_linear`.
- Remap finish returns component count: 3 for RGB-like output, 4 for CMYK/4-component RenderTable output.
- ABC remap preserves original color-space values in `pdc->ccolor`.

## Dependencies
Uses CIE cache structures, Ghostscript color-space internals, imager state, device color remapping, arithmetic helpers, and lookup-table interpolation.

## Research Notes
This file assumes the CIE rendering caches are complete or can be completed by `CIE_CHECK_RENDERING`. Its correctness depends heavily on `skipDecodeABC`, `skipDecodeLMN`, `skipPQR`, and `skipEncodeLMN` flags built in the joint caches.
