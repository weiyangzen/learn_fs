# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscie.c

## Role

`gscie.c` implements CIE color rendering cache management for Ghostscript. It builds, samples, completes, and optimizes CIE color space and Color Rendering Dictionary (CRD) caches, then prepares joint caches used by CIE color remapping.

This is rendering/color-management infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_cie_cached_value`
- `gx_init_CIE`
- `gx_restrict_CIEDEFG`
- `gx_restrict_CIEDEF`
- `gx_restrict_CIEABC`
- `gx_restrict_CIEA`
- `gx_install_CIEDEFG`
- `gx_install_CIEDEF`
- `gx_install_CIEABC`
- `gx_install_CIEA`
- `gx_cie_load_common_cache`
- `gx_cie_common_complete`
- `gs_cie_defg_complete`
- `gs_cie_def_complete`
- `gs_cie_abc_complete`
- `gs_cie_a_complete`
- `gs_setcolorrendering`
- `gs_currentcolorrendering`
- `gx_currentciecaches`
- `gs_cie_cache_init`
- `gs_cie_render_init`
- `gs_cie_render_sample`
- `gs_cie_render_complete`
- `gs_cie_cache_to_fracs`
- `gs_cie_cs_common`
- `gs_cie_cs_complete`
- `gs_cie_jc_complete`
- `gs_cie_compute_points_sd`
- `gx_cie_to_xyz_alloc`
- `gx_cie_to_xyz_free`

## Core Behavior

The file defines default CIE decode/encode functions, default ranges, default matrices, and cache-backed substitutes for DecodeA, DecodeABC, DecodeDEF, DecodeDEFG, and DecodeLMN.

Cache loading is driven by `CIE_LOAD_CACHE_BODY`, which samples client procedures over computed sample domains and records whether a function is identity. Linear-cache detection then marks caches that can be folded into matrix operations.

CIE color installation loads Decode caches, initializes common LMN caches, completes derived vector caches, and invalidates or rebuilds joint caches as needed. DEF and DEFG spaces additionally scale DecodeDEF/DecodeDEFG values into lookup-table dimensions.

CRD handling progresses through explicit statuses:

- `gs_cie_render_init`: initializes matrices, inverse mappings, derived domains, and source/destination white/black points.
- `gs_cie_render_sample`: samples EncodeLMN, EncodeABC, and RenderTable.T functions.
- `gs_cie_render_complete`: restricts sampled values, converts final caches to fracs or table indices, and folds EncodeABC cache scaling into `MatrixABCEncode`.

Joint caches combine the current CIE color space and CRD. `cie_joint_caches_complete` works backward through the mapping pipeline and folds identity steps where possible when `OPTIMIZE_CIE_MAPPING` is enabled.

`gx_cie_to_xyz_alloc` builds a minimal imager state and joint cache for CIE-to-XYZ conversion, used by PDF writing paths.

## Dependencies

Includes Ghostscript color, CIE, matrix, device, imager state, serialization, and arithmetic internals: `gxcspace.h`, `gxcie.h`, `gxcmap.h`, `gzstate.h`, `gsicc.h`, and related math/memory support.

## Notable Risks

- `cie_invert3` divides by determinant without a visible zero/singularity guard.
- Several cache completion routines are explicitly “not idempotent”; callers must honor status ordering.
- Optimized folding depends on exact identity/linearity detection and may alter numerical behavior near interpolation thresholds.
- `gx_cie_to_xyz_alloc` sets `pis->cie_render` to a non-null sentinel pointer only to satisfy checks; the sentinel must never be dereferenced.
