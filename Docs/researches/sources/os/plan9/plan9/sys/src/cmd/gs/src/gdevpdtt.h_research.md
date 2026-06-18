# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtt.h

## Role

`gdevpdtt.h` is the internal interface between pdfwrite text processing files: `gdevpdtt.c`, `gdevpdtc.c`, and `gdevpdte.c`.

## Key Definitions

- Documents six coordinate systems used by pdfwrite text: PostScript user space, device space, PDF user space, font design space, PDF unscaled text space, and PDF text space.
- Defines `pdf_char_glyph_pairs_t`, a variable-length glyph/code table with no pointers.
- Defines `pdf_text_enum_t`, extending Ghostscript text enumeration with fallback enumerator state, origin, Type 3 charproc flags, CDevProc result storage, and glyph-pair collection.
- Defines `pdf_text_process_state_t` for stack-only derived font/text state.
- Defines `pdf_glyph_width_t` and `pdf_glyph_widths_t` for PDF width-array widths and real rendering widths.

## Exported Interfaces

The header declares utilities for font matrices, encoding compatibility, font-resource lookup/allocation, CID/Type 0 resource creation, attached-resource cache access, Type 3 resource creation, text state update, glyph widths, fallback setup, font-kind checks, glyph-to-char encoding, ToUnicode additions, text width modification, and current-point shifting.

## Dependencies

It assumes prior definitions from the pdfwrite text/font stack, especially `gdevpdt.h`, `pdf_font_resource_t`, `pdf_text_state_values_t`, Ghostscript font/text types, and the process-text implementations in sibling files.

## Risks And Invariants

- The coordinate-system comments are operational design documentation; changing text matrix or width code without preserving these mappings risks subtle PDF text placement bugs.
- `pdf_char_glyph_pairs_t` must remain pointer-free because it is variable length and managed as a raw allocation.
- The process procedure signature must remain compatible across `gdevpdtt.c`, `gdevpdtc.c`, and `gdevpdte.c`.
