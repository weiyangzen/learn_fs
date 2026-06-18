# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/postscript.c

## Summary
`postscript.c` is the PostScript backend. It emits DSC headers/trailers, font re-encoding prologs, page flow, headers/footers, formatted text, and EPS-wrapped images.

## Main Responsibilities
- Initializes page size, orientation, encoding, image level, and page counters.
- Emits PostScript document headers, creator/date metadata, bounding boxes, font lists, and page setup.
- Provides ISO-8859-1, ISO-8859-2, and ISO-8859-5 font re-encoding data.
- Handles section-aware headers/footers and starts new pages when body text reaches footer space.
- Writes text strings with PostScript escaping, underline/strike rendering, superscript/subscript movement, font changes, and RGB colors.
- Emits EPS image wrappers for JPEG, PNG, DIB, and fallback images using ASCII85/DCT/Flate/filter pipelines.
- Supports dummy image boxes when image data cannot be emitted.

## Key Dependencies
Uses output alignment helpers, metadata/header/footer getters, font-table APIs, image translators, color conversion, time/user environment data, and geometry helpers.

## Filesystem Relevance
Writes PostScript to `stdout`; reads user name from environment. No filesystem metadata handling.

## Notes
PostScript UTF-8 is unsupported. Image output has a Ghostscript-special PNG predictor mode.
