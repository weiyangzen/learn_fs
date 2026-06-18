# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfk.c

Ghostscript `pdfwrite` Lab and ICCBased color-space writer. It copies existing ICC profiles and synthesizes ICC profiles for CIEBased spaces that cannot be represented directly as PDF Cal/Lab spaces.

Key behavior:
- Adds `/Range` arrays to CIE-derived dictionaries, optionally clamping to ICC-compatible `[0,1]`.
- Uses Ghostscript CIE-to-XYZ concretization for Lab range discovery and ICC lookup-table generation.
- Provides XYZ-to-Lab helpers and `pdf_put_lab_color_space`.
- Keeps arbitrary CIE-to-Lab conversion disabled, returning `rangecheck`.
- `pdf_make_iccbased` constructs a PDF `/ICCBased` array and stream dictionary with `/N`, optional `/Range`, and optional `/Alternate`.
- `pdf_iccbased_color_space` copies an existing ICC profile stream from a Ghostscript CIEICC space into PDF.
- Synthesizes ICC profiles manually because the available ICC library requires random access to output streams.
- Emits ICC headers, table directories, description, white point, copyright, TRC/XYZ tables, or sampled `A2B0` mft2 lookup tables.
- Uses TRC plus XYZ tables for simple one-step CIEBasedABC cases; otherwise samples a multidimensional A2B lookup table into XYZ output.
- Returns range-scaling information for CIE inputs outside `[0,1]` so callers can adjust image Decode values.
- `pdf_convert_cie_space` chooses Lab conversion for PDF < 1.3 and synthesized ICCBased conversion for PDF 1.3+.

Research notes:
- Synthesized ICC profiles are small ad hoc profiles with required tags and fixed metadata.
- The A2B lookup limits total CLUT entries with `MAX_CLUT_ENTRIES`.
- For PDF 1.2 or earlier, general CIE conversion remains effectively unsupported because Lab conversion immediately returns `rangecheck`.
