# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdft.c

## Purpose

`gdevpdft.c` handles PDF 1.4 transparency compositor operations for the pdfwrite driver. It converts Ghostscript PDF14 transparency group and soft-mask operations into PDF group dictionaries, Form XObjects, soft-mask dictionaries, and page group references when transparency output is enabled.

This is graphics/PDF emission code, not filesystem code.

## Main Entry Point

- `gdev_pdf_create_compositor(...)`: intercepts `GX_COMPOSITOR_PDF14_TRANS` operations when `HaveTransparency` is true and `CompatibilityLevel >= 1.4`; otherwise delegates to `psdf_create_compositor`.

Handled PDF14 operations:

- `PDF14_PUSH_DEVICE`
- `PDF14_POP_DEVICE`
- `PDF14_BEGIN_TRANS_GROUP`
- `PDF14_END_TRANS_GROUP`
- `PDF14_INIT_TRANS_MASK`
- `PDF14_BEGIN_TRANS_MASK`
- `PDF14_END_TRANS_MASK`
- `PDF14_SET_BLEND_PARAMS`

## Transparency Group Flow

- `pdf_make_group_dict` creates a `/Group` dictionary resource with:
  - `/Type /Group`
  - `/S /Transparency`
  - optional `/I true`
  - optional `/K true`
  - optional `/CS` based on current graphics-state color space.
- `pdf_begin_transparency_group`:
  - opens the current page/stream,
  - emits pending clip path if necessary,
  - for page-level groups stores `group_id` on the current page,
  - for nested groups prepares graphics state, enters an XObject substream, and writes a Form XObject dictionary through `pdf_make_form_dict`.
- `pdf_end_transparency_group`:
  - leaves page-level groups open for page finalization,
  - or closes nested substreams, substitutes/deduplicates the XObject resource, and emits `/Rname Do`.

## Soft Mask Flow

- `pdf_make_soft_mask_dict` creates a soft-mask dictionary resource with:
  - `/S /Alpha` or `/S /Luminosity`
  - optional `/BC`
  - optional `/TR` transfer function reference.
- `pdf_begin_transparency_mask`:
  - for image masks sets `pdev->image_mask_skip` to avoid installing a transparency buffer while still allowing image enumeration.
  - for non-image masks creates a soft-mask dictionary and begins a transparency group.
- `pdf_end_transparency_mask`:
  - clears `image_mask_skip` for image masks.
  - for non-image masks closes the group XObject, records it as `/G` in the soft-mask dictionary, substitutes the soft-mask resource, and stores the resulting ID in `pis->soft_mask_id`.

## Additional Functions

- `pdf_make_form_dict` writes Form XObject keys such as `/Type /XObject`, `/Subtype /Form`, `/FormType 1`, `/Matrix`, `/BBox`, and `/Group`.
- `pdf_set_blend_params` is a stub returning success.
- Device transparency method stubs:
  - `gdev_pdf_begin_transparency_group`
  - `gdev_pdf_end_transparency_group`
  - `gdev_pdf_begin_transparency_mask`
  - `gdev_pdf_end_transparency_mask`
  - `gdev_pdf_discard_transparency_layer`

## Risks and Limitations

- Blend parameter setting is not implemented.
- Several device methods are stubs because comments say they are apparently never called.
- Image soft-mask handling intentionally enumerates mask images without creating a reference, relying on later duplicate-image recognition.
- Error paths around resource substitution can return success in one case after `pdf_substitute_resource` fails in `pdf_end_transparency_mask`, which is suspicious.
- Transparency is gated on PDF 1.4 compatibility and `HaveTransparency`; lower compatibility falls back to the generic psdf compositor.
