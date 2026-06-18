# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdcrd.c

Sample helper for devices that expose a PostScript CIE Color Rendering Dictionary through device parameters.

Key responsibilities:
- Defines sample CRD constants: white point, PQR/LMN ranges, MatrixABC, encode/transform procedures, and a simple render table.
- Implements `sample_device_crd_get_params`.
- Writes a constant `CRDName` parameter when requested.
- Builds and initializes a `gs_cie_render` structure when the named CRD parameter is requested.
- Writes the CRD through `param_write_cie_render1`.
- Optionally exposes the address of the sample `TransformPQR` procedure as a string parameter.

Important behavior:
- The sample CRD mostly uses default PostScript values with optional "dented" transform/encode procedures.
- `DENT` is currently neutral because `dent_PQR` and `dent_LMN` are `1.0`.
- `bit_EncodeABC_proc` applies `pow(max(in, 0), 0.45)`.
- Render table data is a no-op 2x2x2 RGB cube.
- Built CRDs are reference-counted and released after writing to the parameter list.

Dependencies:
- Ghostscript CIE/color rendering internals: `gscspace.h`, `gscrd.h`, `gscrdp.h`, parameter APIs, client device APIs, memory/string helpers.

Notable risks:
- Comments explicitly call out that storing/exporting a procedure address through an allocated string is a shortcut and not recommended.
- This is sample code, not a full device-specific CRD management framework.
- The optional procedure-address parameter is process/address-space specific and not portable as serialized data.
