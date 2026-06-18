# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfx.h

## Purpose
Internal master header for the Ghostscript `pdfwrite` driver. It defines the PDF device state, resource model, page/object bookkeeping, temporary stream files, encryption/data-stream helpers, pdfmark hooks, and exported cross-module entry points.

## Main Definitions
- Defines output contexts: `PDF_IN_NONE`, `PDF_IN_STREAM`, `PDF_IN_TEXT`, `PDF_IN_STRING`.
- Declares abstract Cos object types and resource types, including standard resources and pseudo-resources such as `resourceCharProc`, `resourceCIDFont`, `resourceCMap`, and `resourceFontDescriptor`.
- Defines `pdf_resource_t`, `pdf_x_object_t`, `pdf_procset_t`, outline/article/page structs, temp-file structs, font-cache structs, viewer state, and substream save records.
- Defines the central `gx_device_pdf_s`, including distiller parameters, encryption state, temp files, object IDs, page/resource lists, text state, named-object namespaces, font cache, clipping state, graphics viewer stack, substream stack, and image-mask conversion state.
- Provides GC descriptor macros for resources, pages, substream state, masked-image converters, and the PDF device.

## Integration
- Used by nearly every PDF backend module as the internal contract for `gx_device_pdf`.
- Text/font modules in this group rely on `pdev->text`, resource chains, substream state, `used_mask`, `substream_Resources`, `font3`, `accumulating_substream_resource`, and stream/object helpers declared here.
- Declares device procedures implemented across `gdevpdf*.c`, including drawing, images, params, text, patterns, transparency, and color spaces.

## APIs Declared
- Document/object/page operations: `pdf_open_document`, `pdf_obj_ref`, `pdf_open_obj`, `pdf_begin_obj`, `pdf_end_obj`, `pdf_open_page`, `pdf_current_page`.
- Resource operations: allocation, lookup, substitution, cancellation, writing, freeing, reversing chains, and page-resource storage.
- Data/encryption operations: `pdf_begin_data_stream`, filter attachment, `pdf_begin_data`, `pdf_end_data`, `pdf_begin_encrypt`, `pdf_encrypt_init`.
- Output helpers: matrix/name/string/value writers, function writers, font bounding-box writer, masked-image conversion helpers.
- pdfmark and named-object APIs.
- Text-module bridge APIs: text data allocation/reset, bitmap CharProc handling, Type 3 accumulation, substream enter/exit, and text context transitions.

## Risks and Notes
- Contains explicit “dangerous pointer” fields (`pte`, `cgp`) that point from global to local memory and must not be traced by the garbage collector.
- `MAX_USER_COORD`, outline depth, destination-string size, and viewer stack depth encode Acrobat/PDF compatibility constraints.
- Resource identity depends on `gs_id_hash` chains and object IDs; incorrect resource ownership can leak or duplicate PDF objects.
- Substream save/restore covers many fields; missing a field would corrupt nested patterns, Type 3 charprocs, masks, or global object accumulation.
