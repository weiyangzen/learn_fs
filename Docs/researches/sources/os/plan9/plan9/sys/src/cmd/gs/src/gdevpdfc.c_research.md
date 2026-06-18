# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfc.c

Ghostscript `pdfwrite` color-space management. It maps Ghostscript/PostScript color spaces into PDF color-space names, arrays, resource objects, and ProcSet flags.

Key behavior:
- Detects CIE spaces that can be represented directly as `/CalGray`, `/CalRGB`, or `/Lab`.
- Provides `pdf_cspace_init_Device` for DeviceGray/RGB/CMYK initialization by component count.
- Emits `/Separation` and `/DeviceN` color spaces with colorant names, alternate spaces, and scaled tint functions.
- Emits `/Indexed` spaces, including procedure-derived palettes, PostScript string encoding, PDF 1.2 restrictions, and RGB-to-gray palette optimization.
- Serializes Ghostscript color spaces with `cs_serialize` and deduplicates matching `resourceColorSpace` resources by serialized bytes.
- `pdf_color_space_named` handles Device, Pattern, CIEICC, CIEA, CIEABC, CIEDEF, CIEDEFG, Indexed, DeviceN, and Separation cases.
- Falls back from unsupported ICC or older-PDF ICC paths to alternate spaces when possible.
- Creates cached Pattern color-space resources and sets image ProcSet bits for gray/indexed/color images.

Research notes:
- General CIEBased spaces are not native PDF spaces. This file recognizes direct calibrated/Lab subsets and delegates broader ICC/Lab conversion to `gdevpdfk.c`.
- Most non-parameterless spaces become named PDF resources so they can be reused and registered in resource dictionaries.
- Some unsupported older compatibility-level cases return `rangecheck`.
