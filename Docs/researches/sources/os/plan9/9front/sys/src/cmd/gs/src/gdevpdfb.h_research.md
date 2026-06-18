# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfb.h

Ghostscript `pdfwrite`/`ps2write` device body template. This header is deliberately included multiple times with caller-defined macros to instantiate concrete PDF-like vector devices.

Key contents:
- Defines a `const gx_device_pdf PDF_DEVICE_IDENT` object using `std_device_dci_type_body` and the macro-supplied device name, identity, inline-image limit, and OPDF-read mode.
- Wires the PDF device procedure table to open/close/page output, parameter handling, rectangle/path/stroke/mask/image/text/compositor/transparency/pattern/color-space entry points.
- Initializes `psdf` common defaults, PDF compatibility and page-selection parameters, DSC/EPS handling, optimization flags, character/font options, compression flags, encryption fields, PDF/X/transparency options, clipping/shading/image limits, overprint and transfer identifiers, resource tables, object IDs, page/resource stacks, outline/article/name structures, viewer graphics state, substream state, image-mask state, and other runtime fields.
- Uses `PDF_DEVICE_MaxInlineImageSize` to choose per-device inline image behavior and `PDF_FOR_OPDFREAD` to mark the open-PDF-reader oriented variant.

Notable dependencies:
- Requires surrounding compilation context to define `gx_device_pdf`, `st_device_pdfwrite`, device procedure implementations such as `pdf_open`, `gdev_pdf_fill_path`, `gdev_pdf_begin_typed_image`, and the `psdf_initial_values` macro.
- Assumes macros such as `PDF_DEVICE_NAME`, `PDF_DEVICE_IDENT`, `PDF_DEVICE_MaxInlineImageSize`, and `PDF_FOR_OPDFREAD` are defined before inclusion.

Research notes:
- This is not a conventional guarded header; the leading comment explicitly permits repeated inclusion in a single C file.
- It is a large static initializer rather than executable logic, so behavior comes from the procedure pointers and from the default field values established here.
- The default `MaxClipPathSize` is set to `12000` with a comment noting HP LaserJet 1320 hangs at `14000`.
- This file is Ghostscript PDF output infrastructure, not filesystem code.
