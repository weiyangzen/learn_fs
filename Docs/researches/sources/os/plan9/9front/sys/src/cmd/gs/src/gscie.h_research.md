# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscie.h

## Role

`gscie.h` defines the core data structures, cache layout, procedure types, defaults, constructors, and accessors for Ghostscript CIE color algorithms.

This is rendering/color-management infrastructure, not filesystem code.

## Main Definitions

- CIE cache sizing:
  - `CIE_LOG2_CACHE_SIZE`
  - `gx_cie_cache_size`
  - interpolation macros
  - fixed-vs-float cache value selection
- Vector and matrix types:
  - `gs_vector3`
  - `gs_matrix3`
  - `gs_range3`
  - `gs_range4`
- CIE procedure types:
  - `gs_cie_a_proc`
  - `gs_cie_abc_proc`
  - `gs_cie_def_proc`
  - `gs_cie_defg_proc`
  - `gs_cie_common_proc`
  - `gs_cie_render_proc`
  - `gs_cie_transform_proc`
  - `gs_cie_render_table_proc`
- Cache structures:
  - `cie_cache_floats`
  - `cie_cache_fracs`
  - `cie_cache_ints`
  - `gx_cie_vector_cache`
  - `gx_cie_vector_cache3_t`
- CIE color structures:
  - `gs_cie_common`
  - `gs_cie_a`
  - `gs_cie_abc`
  - `gs_cie_def`
  - `gs_cie_defg`
- CRD structures:
  - `gs_cie_render`
  - `gs_cie_render_table_t`
  - `gx_cie_joint_caches`

## Public API Surface

Declares constructors for CIEBasedA, CIEBasedABC, CIEBasedDEF, and CIEBasedDEFG color spaces, plus lookup-table setup and CRD/cache completion functions.

It also declares CIE cache utilities, joint-cache completion, sampled-loop helpers, and `gx_serialize_cie_common_elements`.

## Important Design Notes

Matrices are stored in column order and multiplied as column-vector transforms. The header explicitly notes that composing M1 followed by M2 requires computing `M2 * M1`.

The cache system assumes monotonic client functions with known domains so procedure callbacks can be sampled up front and avoided in rendering hot paths.

The constructor comment warns that CIE parameter structures are created with reference count 1, while `gs_setcolorspace` increments again; clients are expected to adjust counts afterward. The comment labels this as an API bug.

## Notable Risks

- Heavy reliance on structural “puns” between CIEA/ABC/DEF/DEFG parameter layouts makes field ordering critical.
- `gs_cie_a_RangeA` is defined twice.
- Several comments describe status preconditions, but implementation in `gscie.c` mostly treats completion calls as idempotent rather than rejecting out-of-order states.
