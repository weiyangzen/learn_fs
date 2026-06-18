# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdti.h

Bitmap font interface header for `pdfwrite`. It exposes synthesized Type 3 bitmap font operations and internal Type 3 content-writing hooks.

Key contents:
- Documents bitmap fonts as internally created Type 3 fonts whose CharProcs contain a single bitmap image at device resolution.
- Forward-declares `pdf_bitmap_fonts_t`.
- Declares page-close text update, bitmap image Y-offset calculation, CharProc begin/end, and image-as-character emission for bitmap copy code.
- Declares bitmap-font bookkeeping allocation.
- Declares writing the shared bitmap font Encoding object.
- Declares writing the contents of a Type 3 bitmap font resource.

Notable dependencies:
- Includes `gdevpdt.h`, giving access to the outer text/font interface and PDF device types.
- Implemented by `gdevpdti.c` and used by bitmap/text output code.

Research notes:
- This is a small private interface for the bitmap/Type 3 side of the text subsystem.
- It does not define the internal bitmap-font or charproc structures; those live in the implementation file.
- No filesystem behavior is present.
