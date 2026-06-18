# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdcrd.c

Sample implementation for exposing a device Color Rendering Dictionary through Ghostscript device parameters.

Key behavior:
- Defines default-ish CIE rendering data: white point, PQR/LMN ranges, transform/encode procedures, ABC matrix, gamma-like ABC encoding, and dummy render tables.
- `sample_device_crd_get_params` conditionally writes:
  - `CRDName`
  - a built CIE Render1 object under the requested CRD parameter name
  - a serialized pointer-sized procedure address string for the sample PQR transform proc name.
- Builds and initializes a `gs_cie_render` object with `gs_cie_render1_build` and `gs_cie_render1_initialize`, writes it with `param_write_cie_render1`, and decrements the reference.

Notable dependencies:
- Ghostscript CIE color/rendering internals: `gscspace.h`, `gscrd.h`, `gscrdp.h`, `gxdevcli.h`.
- Header `gdevdcrd.h`.

Research notes:
- Comments identify it as sample code; a settable `CRDName` is left as an exercise.
- The static procedure-address export is explicitly discouraged in comments and is a shortcut for sample behavior.
