# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtd.h

FontDescriptor API header for `pdfwrite`. It documents descriptor lifetime, sharing, font-name rules, metric computation, embedded font finalization, and writing.

Key contents:
- Explains that FontDescriptors are pseudo-resources that persist until device close and may be shared by multiple Font resources.
- Documents the subsystem's one-to-one FontDescriptor/BaseFont relationship.
- Documents the rule that a descriptor's `FontName` must match the `BaseFont` of referencing Font/CIDFont resources and is set alongside the font resource name.
- Declares descriptor allocation, ID/type/embed/subset accessors, descriptor and base font-name accessors, copied font access, complete-font dropping, glyph-use recording, metric computation, descriptor finalization, descriptor iteration/finalization helper, descriptor writing, and component release.

Notable dependencies:
- Includes `gdevpdtx.h` and `gdevpdtb.h`.
- References `gx_device_pdf`, `gs_font_base`, `gs_glyph`, and `pdf_font_descriptor_t`.

Research notes:
- This is a private font subsystem interface, mostly consumed by font-resource and text-processing code.
- Descriptor writing is intentionally delayed until font subsetting and CharSet/CIDSet decisions are known.
- No filesystem behavior is present.
