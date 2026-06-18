# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfb.h

Ghostscript `pdfwrite`/`ps2write` device body template. This header is intentionally included with caller-defined macros to instantiate concrete PDF-like vector devices.

Key contents:
- Defines a `const gx_device_pdf PDF_DEVICE_IDENT` initializer using the macro-supplied device name, identifier, inline-image threshold, and OPDF-read flag.
- Wires the PDF device procedure table to open/close/page output, parameters, rectangle/path/stroke/mask/image/text/compositor/transparency/pattern/color-space entry points.
- Initializes PDF writer defaults for compatibility level, page selection, optimization, DSC/EPS behavior, font compression, encryption, PDF/X, clipping/shading/image limits, resource tables, object IDs, outlines, named objects, graphics-state stacks, substreams, and image-mask state.
- Sets `MaxClipPathSize` to `12000`, with a comment noting a LaserJet compatibility failure at `14000`.

Research notes:
- This is a static device initializer rather than executable logic.
- It is not guarded by include macros because repeated inclusion is part of the design.
- This is Ghostscript PDF output infrastructure, not filesystem code.
