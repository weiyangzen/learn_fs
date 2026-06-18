# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfv.c

Pattern and shading color output for Ghostscript `pdfwrite`. It writes PatternType 1 tiling patterns, PatternType 2 shading patterns, image-backed pattern masks, and PDF shading dictionaries/streams.

Key behavior:
- Defines mesh shading coordinate and component encoding ranges, including Acrobat coordinate-range constraints.
- Provides a COS helper for writing matrix arrays.
- Validates image-pattern tile sizes against Acrobat’s approximate 64 KB image pattern limit.
- Creates PatternType 1 resources that reference image XObjects, with `/PatternType`, `/PaintType`, `/TilingType`, `/Resources`, `/BBox`, `/Matrix`, `/XStep`, `/YStep`, and a small content stream invoking the image XObject.
- Stores high-level PatternType 1 parameters from Ghostscript pattern instances, compensating for shifted bitmap origins and device resolution scaling.
- Writes imagemask resources for uncolored pattern masks, inverting Y because pattern masks are in device coordinates.
- Emits uncolored patterns, optimizing all-ones masks into pure-color output when no pattern stream is needed.
- Emits colored patterns, including optimization of masked colored patterns into uncolored pure-color patterns when all masked pixels share one color.
- Rejects masked image patterns for compatibility levels below PDF 1.3.
- Handles high-level pattern streams by finding/deduplicating already-created Pattern resources.
- Writes common shading dictionary keys: `/ShadingType`, `/AntiAlias`, `/ColorSpace`, optional `/Background`, and optional `/BBox`.
- Writes scalar shadings:
  - Function-based
  - Axial
  - Radial
- Writes optional shading `/Function` entries, with range scaling when needed.
- Converts array-backed mesh data into packed binary PDF shading streams with 24-bit coordinates, 16-bit components, and 8-bit flags.
- Handles free-form Gouraud triangle, lattice-form Gouraud triangle, Coons patch, and tensor-product patch shadings.
- Writes PatternType 2 shading pattern dictionaries with `/PatternType 2`, `/Shading`, and transformed `/Matrix`.
- Exposes `gdev_pdf_include_color_space` to register a color space resource by name.

Notable dependencies:
- Ghostscript pattern/shading APIs: `gsiparm3.h`, `gsptype2.h`, `gxpcolor.h`, and `gxshade.h`.
- PDF color-space, image-writer, resource, and COS helpers from `gdevpdfg.h`, `gdevpdfx.h`, and `gdevpdfo.h`.

Research notes:
- Pattern output is tightly coupled to image XObject creation from the image-writing modules.
- Mesh data handling distinguishes array data sources from stream data sources; array data is re-encoded into PDF-friendly packed binary.
- Several comments document viewer compatibility limits rather than core PDF spec limitations.
- This file handles PDF graphics resources and color output, not filesystem functionality.
