# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdft.c

Ghostscript `pdfwrite` transparency compositor bridge. It converts Ghostscript PDF 1.4 transparency compositor operations into PDF group, form XObject, and soft-mask resources when transparency output is available.

Key behavior:
- Builds soft-mask dictionaries with `/S /Alpha` or `/S /Luminosity`, optional `/BC` background color arrays, and optional `/TR` transfer function references.
- Builds transparency group dictionaries with `/Type /Group`, `/S /Transparency`, optional `/I`, optional `/K`, and optional `/CS` based on the current Ghostscript color space.
- Deduplicates group resources through `pdf_substitute_resource`.
- Builds form XObject dictionaries for nested transparency groups, including transformed `/BBox`, `/Subtype /Form`, `/FormType 1`, identity `/Matrix`, and `/Group`.
- Begins transparency groups by opening the page, emitting needed clip paths, and either recording a page group ID or entering an XObject substream for nested groups.
- Ends transparency groups by closing the substream, deduplicating the XObject resource, and emitting `/R# Do` for nested groups.
- Begins transparency masks either by setting an image-mask skip flag for image masks or by creating a soft-mask dictionary and nested group.
- Ends transparency masks by closing the accumulated group XObject, storing it as `/G` in the soft-mask dictionary, deduplicating the soft-mask dictionary, and recording `pis->soft_mask_id`.
- `gdev_pdf_create_compositor` intercepts `GX_COMPOSITOR_PDF14_TRANS` operations for PDF 1.4+ when transparency is enabled; otherwise it delegates to `psdf_create_compositor`.
- Provides stub device methods for older transparency device hooks that the comments say are not expected to be called.

Notable dependencies:
- Ghostscript transparency types from `gstrans.h`.
- Color-space, drawing-state, resource, and COS helpers from `gdevpdfx.h`, `gdevpdfg.h`, and `gdevpdfo.h`.

Research notes:
- Transparency output is gated by `HaveTransparency` and `CompatibilityLevel >= 1.4`.
- Image soft masks are handled with a documented double-enumeration workaround so high-level image handling can deduplicate the actual image stream later.
- `pdf_set_blend_params` is currently a no-op.
- This file is PDF transparency output support, unrelated to filesystem behavior.
