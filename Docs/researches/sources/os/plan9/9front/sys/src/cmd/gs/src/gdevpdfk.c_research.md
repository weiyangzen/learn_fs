# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfk.c

Ghostscript `pdfwrite` Lab and ICCBased color-space writer. It copies existing ICC profiles and synthesizes minimal ICC profiles for CIEBased color spaces that cannot be represented directly as PDF Cal/Lab spaces.

Key behavior:
- Adds `/Range` arrays to CIE-derived dictionaries, with optional clamping to ICC-compatible `[0,1]` component ranges.
- Uses Ghostscript CIE-to-XYZ concretization to evaluate arbitrary CIE color spaces for Lab range discovery or ICC lookup-table generation.
- Provides Lab helpers for XYZ-to-Lab conversion and `pdf_put_lab_color_space`; arbitrary CIE-to-Lab conversion is present but intentionally disabled with a rangecheck.
- `pdf_make_iccbased` constructs a PDF `/ICCBased` array and stream dictionary, writes `/N`, optional `/Range`, and optional `/Alternate`, and reports when input scaling is needed.
- `pdf_iccbased_color_space` copies an existing ICC profile stream from a Ghostscript CIEICC color space into a PDF ICCBased stream.
- Builds synthesized ICC profiles by hand because the comment says the available `icclib` requires random access to the output stream.
- Emits ICC header, table directory, description, white-point, copyright, TRC/XYZ tables, or a sampled `A2B0` mft2 lookup table.
- Uses TRC plus XYZ tables for simple CIEBasedABC cases described by `ONE_STEP_ABC` or `ONE_STEP_LMN`; otherwise samples a multidimensional A2B0 lookup table into XYZ output.
- Handles CIE input ranges that exceed `[0,1]` by returning range-scaling information to callers, allowing image Decode values to be adjusted upstream.
- `pdf_convert_cie_space` chooses Lab conversion for PDF < 1.3 and synthesized ICCBased conversion for PDF 1.3+.

Notable dependencies:
- CIE and ICC internals from `gxcspace.h`, `gxcie.h`, and `gsicc.h`.
- Cross-file interfaces from `gdevpdfc.h`, color-space declarations from `gdevpdfg.h`, and object writing from `gdevpdfo.h`.

Research notes:
- The synthesized ICC profile is intentionally small and “adhoc”; it includes required tags and fixed metadata but is constructed directly into the COS stream.
- The A2B lookup table limits total CLUT entries with `MAX_CLUT_ENTRIES` and computes per-axis sample counts based on component count.
- The code includes a subtle ICC-specific normalization note: A2B0 XYZ table values are scaled against `1 + 32767/32768`, not exactly `[0,1]`.
- For PDF 1.2 or earlier, general CIE conversion effectively remains unsupported because `pdf_convert_cie_to_lab` immediately returns rangecheck.
