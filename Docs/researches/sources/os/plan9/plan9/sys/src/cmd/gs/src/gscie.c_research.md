# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscie.c

## Purpose
Core CIE color rendering cache management for Ghostscript. It samples CIE dictionary procedures, builds scalar/vector caches, prepares Color Rendering Dictionaries, and lazily completes joint caches that depend on both the current CIE color space and the current CRD.

## Key Behavior
- Defines default Decode/Encode/Transform/RenderTable procedures and cache-backed procedure variants.
- Initializes and restricts CIEA, CIEABC, CIEDEF, and CIEDEFG client colors.
- Loads DecodeA/ABC/DEF/DEFG/LMN caches when CIE spaces are installed.
- Detects identity and linear cached functions to simplify later mapping.
- Converts scalar caches into vector caches pre-multiplied by matrices.
- Computes interpolation ranges for numerically sensitive cache sections.
- Implements `gs_setcolorrendering`, `gs_currentcolorrendering`, and reference-counted joint-cache unsharing.
- Initializes, samples, and completes CRDs, including EncodeLMN/EncodeABC caches and optional RenderTable/T caches.
- Builds joint caches by folding CIE pipeline stages when identity procedures allow it.
- Provides a special CIE-to-XYZ imager state path used by high-level output code.

## Important Details
- The CIE mapping pipeline is optimized by folding steps backward when DecodeLMN, TransformPQR, or EncodeLMN are identity.
- Cache domain setup adjusts ranges crossing zero so zero maps exactly to a cache slot, avoiding common color default anomalies.
- `gs_cie_jc_complete` reuses completed joint caches by color-space ID and CRD ID where possible.
- `gx_cie_to_xyz_alloc` creates a reduced imager state whose finish procedure returns XYZ-like intermediate values rather than final device color.

## Dependencies
Uses CIE structures from `gscie.h`/`gxcie.h`, color-space and graphics-state internals, device color mapping, matrix math, GC/refcount helpers, and ICC integration hooks.

## Research Notes
This is the main preparation layer; actual hot-path color mapping is in `gsciemap.c`. Several comments mark historical limitations, including preloaded TransformPQR caches preventing range adjustment and XYZ remapping clamping values to `[0..1]`.
