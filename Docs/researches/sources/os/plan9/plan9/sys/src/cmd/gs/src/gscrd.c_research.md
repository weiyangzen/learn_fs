# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrd.c

## Purpose
Creates and initializes Ghostscript CIE Color Rendering Dictionaries.

## Key Behavior
- Defines the GC descriptor for `gs_cie_render`.
- Provides default CRD procedures:
  - identity TransformPQR,
  - cache-marker TransformPQR,
  - identity Encode and RenderTable.T.
- Defines cache-backed EncodeLMN/EncodeABC and RenderTable.T procedures.
- Implements TransformPQR procedure-name lookup through device parameters:
  - copies a device prototype,
  - requests the named parameter,
  - reads back a procedure address stored as a string.
- Exposes default CRD procedure constants used by other files.
- `gs_cie_render1_build` allocates and minimally initializes a CRD.
- `gs_cie_render1_init_from` copies full CRD parameters and optionally copies already-sampled cached values from another CRD.
- `gs_cie_render1_initialize` is a convenience wrapper without cache copying.

## Important Details
- The CRD reference-count comment repeats the same API caveat as CIE color spaces: clients usually need to decrement after installing.
- `TransformPQR_from_cache` is a marker; it cannot perform actual lookup because the TransformPQR cache lives in joint caches, not in the CRD.
- Driver-specific TransformPQR lookup depends on matching `driver_name` against registered device names.

## Dependencies
Uses device list/device parameter APIs, C parameter lists, CIE structures, color rendering APIs, refcount/GC helpers, and matrix defaults.

## Research Notes
This file defines CRD object construction; cache sampling/completion is handled by `gscie.c`, and parameter dictionary serialization by `gscrdp.c`.
