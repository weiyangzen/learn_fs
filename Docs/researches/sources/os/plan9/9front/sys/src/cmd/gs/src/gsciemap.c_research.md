# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsciemap.c

## Role

`gsciemap.c` is the runtime CIE color rendering hot path. It maps CIEBasedA/ABC/DEF/DEFG client colors through precomputed caches, CRD transforms, render tables, and final concrete RGB/CMYK remapping.

This is rendering/color-management infrastructure, not filesystem code.

## Main Public Interfaces

- `gx_concretize_CIEDEFG`
- `gx_concretize_CIEDEF`
- `gx_remap_CIEABC`
- `gx_concretize_CIEABC`
- `gx_concretize_CIEA`
- `gx_cie_remap_finish`
- `gx_cie_real_remap_finish`
- `gx_cie_xyz_remap_finish`

## Core Behavior

For CIEBasedDEF and CIEBasedDEFG, input components are decoded through cached DecodeDEF/DecodeDEFG values, clamped and scaled into lookup-table coordinates, interpolated through `gx_color_interpolate_linear`, converted into ABC values, optionally passed through DecodeABC/MatrixABC, then finished through the joint CIE pipeline.

For CIEBasedABC and CIEBasedA, the code maps input values directly into cached vector forms before invoking the remap finish procedure.

`gx_cie_real_remap_finish` applies the remaining joint-cache pipeline:

- DecodeLMN / MatrixLMN / MatrixPQR
- TransformPQR / inverse PQR / MatrixLMN
- EncodeLMN / MatrixABC
- EncodeABC
- optional RenderTable lookup and RenderTable.T mapping

It returns 3 for RGB output or 4 for CMYK output.

`gx_cie_xyz_remap_finish` is a special endpoint for CIE-to-XYZ export; it clamps XYZ values into fracs.

## Performance Design

The file uses cache-index macros to avoid function-call overhead in non-debug builds. `cie_lookup_mult3` supports interpolation only inside precomputed interpolation ranges and otherwise performs direct lookup and cached vector summation.

## Dependencies

Uses CIE definitions from `gxcie.h`, color remapping from `gxcmap.h`, device color operations, imager state, and fixed/fraction arithmetic.

## Notable Risks

- The code assumes `CIE_CHECK_RENDERING` establishes valid CIE rendering state before cache use.
- Index arithmetic is performance-oriented and depends on cache base/factor/limit correctness from `gscie.c`.
- The non-interpolating render-table path is compiled out when `CIE_RENDER_TABLE_INTERPOLATE` is defined, so both variants must be maintained carefully.
