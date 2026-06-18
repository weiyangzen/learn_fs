# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrdp.c

## Purpose
Reads and writes device-specified CIE Color Rendering Dictionaries as parameter dictionaries.

## Key Behavior
- Writes vectors, matrices, ranges, and sampled procedure values into parameter lists.
- `param_write_cie_render1` writes a CRD as a named dictionary parameter.
- `param_put_cie_render1` writes the CRD body directly:
  - `ColorRenderingType`,
  - White/BlackPoint,
  - MatrixPQR/LMN/ABC,
  - RangePQR/LMN/ABC,
  - sampled EncodeLMN/EncodeABC values,
  - optional RenderTable size/table/T sampled values,
  - optional TransformPQR procedure name/data.
- Reads CRDs from named or direct parameter dictionaries.
- Converts sampled EncodeLMN/ABC and RenderTable.T arrays into temporary client-data callbacks.
- Completes CRD initialization/sampling, then replaces those callbacks with cache-backed procedures.

## Important Details
- Only serializable TransformPQR procedures are supported: identity or named device-provided procedure. Arbitrary procedures return `rangecheck`.
- Read path validates RenderTable dimensions and string sizes.
- Temporary `encode_data_t` lives on the stack while CRD caches are being populated; after completion, procedures are switched to `_from_cache`.
- Comments mark questionable persistence handling for TransformPQRData and incomplete RenderTableT writing abstraction.

## Dependencies
Uses CIE/CRD APIs, parameter-list APIs, device names, memory allocation, ranges/matrices, and cache completion from `gscie.c`.

## Research Notes
This file is central to device CRD interoperability. The stack-backed temporary callback scheme is safe only because the CRD is immediately initialized, sampled, and completed before `client_data` is cleared.
