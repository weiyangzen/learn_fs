# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtt.h

Internal pdfwrite text-processing interface shared by `gdevpdtt.c`, `gdevpdtc.c`, and `gdevpdte.c`.

Key behavior:
- Documents the six coordinate systems used by pdfwrite text handling: PostScript user space, device space, PDF user space, font design space, PDF unscaled text space, and PDF text space.
- Defines `pdf_char_glyph_pairs_t`, a variable-length character/glyph collection used to track all chars and not-yet-used glyphs for font-resource compatibility.
- Defines `pdf_text_enum_t`, extending Ghostscript text enumeration with a fallback/default enumerator, text origin, charproc accumulation flags, CDevProc result storage, and a char/glyph pair table.
- Defines `pdf_text_process_state_t`, a stack-only holder for derived PDF text state values plus current font.
- Defines `pdf_glyph_width_t` and `pdf_glyph_widths_t` for width-array values, real rendering widths, vertical origin shifts, and replaced-v-vector state.
- Declares the `PROCESS_TEXT_PROC` signature used by composite, CMap/CID, and plain text processors.
- Exposes `gdevpdtt.c` services for original font matrix/scale, encoding compatibility, font resource lookup/creation, CID font and parent Type 0 resource creation, attached resource lookup, Type 3 resource creation, text state update/sync, glyph-width lookup, default text fallback, font-type tests, Type 3 scale lookup, and current-point shifting.
- Declares processing entry points from `gdevpdtc.c` and `gdevpdte.c`.
- Declares plain-font encoding/text helpers, width modification, ToUnicode mapping, glyph encoding, and text current-point shifting.

Research notes:
- The header is mostly a contract file; the coordinate-system comment is essential context for understanding the matrix math in `gdevpdtt.c`.
- It forms the boundary between text enumeration, font resource management, and downstream plain/composite text processors.
