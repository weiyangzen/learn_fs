# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfx.h

Central private header for Ghostscript's PDF-writing device. It defines the shared `gx_device_pdf` state, resource model, output contexts, page bookkeeping, temporary-file streams, encryption fields, and cross-module procedure declarations used by the `pdfwrite` implementation.

Key contents:
- Defines output stream contexts: `PDF_IN_NONE`, `PDF_IN_STREAM`, `PDF_IN_TEXT`, and `PDF_IN_STRING`.
- Declares abstract COS object types used by the PDF object layer.
- Defines PDF resource types, including standard page resources (`ColorSpace`, `ExtGState`, `Pattern`, `Shading`, `XObject`, `Font`) and internal pseudo-resources (`CharProc`, `CIDFont`, `CMap`, `FontDescriptor`, `Group`, `SoftMaskDict`, `Function`, `Page`).
- Defines common resource fields: linked-list links, resource ID, global/named flags, resource name, usage bitmask, and associated COS object.
- Defines `pdf_x_object_t` for Image/Form/PS XObject resources and `pdf_procset_t` bits for page ProcSet tracking.
- Defines document/page helper structures for outlines, articles, DSC-derived page metadata, saved pages, stream positions, text rotation, and temporary files.
- Defines `pdf_font_cache_elem_t` for cached font-resource attachment, glyph usage, and real-width arrays.
- Defines `pdf_viewer_state`, the driver-side mirror of the emitted viewer graphics state: transfer/halftone IDs, alpha/blend/soft-mask state, overprint flags, saved colors, line parameters, dash pattern, and related state.
- Defines `pdf_substream_save` for saving text state, clip state, viewer state, stream/resource context, and substream flags while accumulating charprocs, patterns, forms, and masks.
- Defines the full `gx_device_pdf_s` structure, including Distiller parameters, compression/encryption settings, DSC flags, temporary files, current page/content IDs, resource chains, named-object dictionaries, NI/namespace stacks, font cache, clipping state, page labels, viewer-state stack, substream stack, pattern/image-mask temporary fields, and ps2write-specific flags.
- Declares GC descriptor macros for `gx_device_pdf`, resource objects, XObjects, local converter devices, and substream save objects.
- Declares driver procedure entry points implemented in other files for bitmap copying, path drawing, images, parameters, text, patterns, color spaces, compositors, and transparency.
- Declares shared utilities for object allocation, page/content stream management, resources, encryption, path clipping, masked-image conversion, matrices, names/strings, filters, data streams, functions, font bbox writing, pdfmark processing, named objects, namespaces, and text module hooks.

Notable dependencies:
- Depends on Ghostscript core device/font/stream headers such as `gxdevice.h`, `gxfont.h`, `gxline.h`, `gxdevmem.h`, `stream.h`, and `gdevpsdf.h`.
- Cross-links to many implementation modules: `gdevpdf*.c` for general PDF output and `gdevpdt*.c` for text/font handling.
- Exposes private resource descriptor names such as `st_pdf_font_resource`, `st_pdf_char_proc`, `st_pdf_font_descriptor`, and `st_pdf_color_space`, which are defined by sibling modules.

Research notes:
- This is the central internal contract for the PDF-writing subsystem; it is not a public API.
- Several comments document viewer compatibility limits, especially Acrobat coordinate limits and viewer stack depth.
- The `pte` and `cgp` members are explicitly dangerous temporary pointers from global to local memory and must not be traced by the garbage collector.
- The file is PDF/vector-output infrastructure, not filesystem code.
