# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfc.c

Ghostscript `pdfwrite` color-space management and color-space resource emission. It maps Ghostscript/PostScript color spaces into PDF color space names, arrays, resources, and supporting functions.

Key behavior:
- Detects simple CIE cases that PDF can represent as `/CalGray`, `/CalRGB`, or `/Lab`, using cached CIE identity/exponential tests and special Lab-space recognition.
- Provides `pdf_cspace_init_Device` for local DeviceGray/RGB/CMYK color-space initialization based on component count.
- Builds `/Separation` and `/DeviceN` color spaces by writing colorant names, alternate spaces, and scaled tint-transform functions.
- Builds `/Indexed` color spaces, including procedure-derived palettes, PostScript string encoding, PDF 1.2 compatibility restrictions, and a gray-palette optimization for RGB indexed data.
- Serializes Ghostscript color-space objects with `cs_serialize`, deduplicates them against existing `resourceColorSpace` entries by serialized bytes, and stores serialized data in `pdf_color_space_t`.
- `pdf_color_space_named` handles DeviceGray/RGB/CMYK, Pattern, CIEICC, CIEA, CIEABC, CIEDEF, CIEDEFG, Indexed, DeviceN, and Separation cases; parameterized spaces become PDF resources and can be returned by resource name.
- Falls back from unsupported CIEICC or unavailable ICC profiles to alternate color spaces when appropriate.
- Creates cached colored and uncolored Pattern color-space resources through `pdf_cs_Pattern_colored`, `pdf_cs_Pattern_uncolored`, and high-level color-space handling for uncolored patterns.
- Updates PDF ProcSet bits for image color spaces, distinguishing bitmap/gray/indexed/color image usage.

Notable dependencies:
- Ghostscript color-space APIs: `gscspace.h`, `gscdevn.h`, `gscie.h`, `gscindex.h`, `gscsepr.h`, `gxcspace.h`, and `gsicc.h`.
- PDF object/resource helpers from `gdevpdfx.h`, `gdevpdfg.h`, `gdevpdfc.h`, and `gdevpdfo.h`.
- CIE conversion and ICCBased creation are split with `gdevpdfk.c` via `pdf_iccbased_color_space`, `pdf_convert_cie_space`, and `pdf_put_lab_color_space`.

Research notes:
- The top comment documents a key design limitation: general CIEBased spaces are not native PDF spaces, so the driver either recognizes direct Cal/Lab subsets or emits ICCBased spaces for PDF 1.3+.
- Lab conversion for arbitrary CIE spaces is intentionally not implemented here; unsupported PDF 1.2-or-earlier CIE conversions return rangecheck through `gdevpdfk.c`.
- `pdf_color_space_named` has several early returns for parameterless Device spaces; most other spaces are resource-backed to allow reuse and resource-dictionary registration.
- Some error paths after allocating serialized color-space bytes return directly without freeing all transient allocations, but the main success path transfers ownership into the `pdf_color_space_t` resource.
