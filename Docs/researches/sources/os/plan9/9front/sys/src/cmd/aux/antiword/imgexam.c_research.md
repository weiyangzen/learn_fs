# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/imgexam.c

This file examines embedded Word image records and derives image metadata.

Key routines:
- DIB/BMP: `bFillPaletteDIB`, `bExamineDIB`.
- JPEG: `iNextMarker`, `bExamineJPEG`.
- PNG: `bFillPalettePNG`, `bExaminePNG`.
- WMF stub: `bExamineWMF`, currently always returns `FALSE`.
- Scaling: `vImage2Papersize` for non-RISC OS builds.
- Word wrappers: `tFind6Image`, `tFind8Image`, and public `eExamineImage`.

Important behavior:
- Supports full metadata for DIB, baseline/extended sequential JPEG, and non-interlaced PNG without alpha.
- Rejects unsupported JPEG modes, unsupported PNG bit/component combinations, invalid BMP compression/bit-depth combinations, and impossible image dimensions.
- Word 8 image search parses Office drawing record types and recognizes EMF, WMF, PICT, JPEG, PNG, and DIB instances.
- Vector/external images can still return minimal information.
- Image dimensions are scaled from Word twips/scaling factors and capped to page bounds for non-RISC OS output.

Dependencies:
- Binary stream readers, PNG chunk constants, image data structures, options/page sizing, and image type enums.

Role in antiword:
- Decides whether an embedded image can be translated fully or represented as a placeholder.
