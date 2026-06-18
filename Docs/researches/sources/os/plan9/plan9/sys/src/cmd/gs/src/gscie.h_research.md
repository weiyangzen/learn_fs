# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscie.h

## Purpose
Defines Ghostscript’s CIE color structures, cache formats, transformation procedure types, CRD representation, joint-cache representation, defaults, constructors, and accessors.

## Key Contents
- Cache configuration:
  - `CIE_LOG2_CACHE_SIZE` defaulting to 9.
  - optional fixed-point cache values when FPU support is poor.
  - interpolation support and thresholds for CIE caches and RenderTables.
- Core math types: `gs_vector3`, column-major `gs_matrix3`, `gs_range3`, and `gs_range4`.
- Procedure types for DecodeA/ABC/DEF/DEFG, DecodeLMN, EncodeLMN/ABC, TransformPQR, and RenderTable.T.
- Scalar cache forms for floats, fracs, and ints; vector caches for matrix-premultiplied values.
- CIE color-space structures for CIEBasedA, ABC, DEF, and DEFG.
- `gs_cie_render`: Color Rendering Dictionary state, including original dictionary fields and derived/cached fields.
- `gx_cie_joint_caches`: shared cache state keyed by color-space ID and CRD ID.
- Sampling helper `SAMPLE_LOOP_VALUE`, cache initialization APIs, CRD state transition APIs, and CIE color-space constructors.

## Important Details
- Matrices are stored in column order and matrix composition is documented as `M2 * M1` for applying `M1` then `M2`.
- DEF and DEFG structures deliberately share the leading ABC/common layout, and the header notes accessors depend on these structure “puns.”
- Constructor comments warn that CIE color-space parameter structures are created with reference count 1, while `gs_setcolorspace` increments again; clients must decrement after setting if they do not want persistent allocation.

## Dependencies
Requires Ghostscript color-space, reference-counting, type, stream/table, and matrix-related headers.

## Research Notes
This header is the contract linking `gscie.c`, `gsciemap.c`, `gscscie.c`, `gscrd.c`, and `gscrdp.c`. It is performance-oriented and encodes many assumptions about cache size, interpolation precision, and shared structure layout.
