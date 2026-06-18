# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtd.h

## Purpose
Defines the FontDescriptor interface for `pdfwrite`.

## Model
- FontDescriptors are pseudo-resources retained until device close.
- Multiple Font resources may share one descriptor.
- In this implementation, FontDescriptors and BaseFonts correspond one-to-one.
- Descriptor `FontName` must match the Font resource `BaseFont`, so naming is coordinated with `gdevpdtf.h` and `gdevpdtb.h`.

## API Surface
- Allocation: `pdf_font_descriptor_alloc`.
- Accessors: descriptor ID, FontType, embedding state, subset state, descriptor name, copied font, base name.
- Glyph tracking: `pdf_font_used_glyph`.
- Metric/output lifecycle:
  - `pdf_compute_font_descriptor`
  - `pdf_finish_FontDescriptor`
  - `pdf_finish_font_descriptors`
  - `pdf_write_FontDescriptor`
  - `pdf_release_FontDescriptor_components`

## Integration
- Includes `gdevpdtx.h` and `gdevpdtb.h`.
- Exposes descriptor operations to font-resource allocation and writing modules.

## Risks and Notes
- The header documents delayed descriptor writing because CharSet depends on final subset contents.
- Descriptor objects are not reference-counted; lifetime relies on all descriptors persisting until device close.
