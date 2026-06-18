# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfg.c

Ghostscript `pdfwrite` graphics-state management. It tracks the PDF viewer state that the emitted content stream will produce, writes color and ExtGState changes, and preserves selected imager state such as transfer functions and halftones.

Key behavior:
- Saves/restores viewer graphics state in `pdev->vgstack`, including transfer IDs, alpha, blend mode, halftone/BG/UCR IDs, overprint, smoothness, text knockout, stroke adjustment, colors, line parameters, and dash pattern.
- Initializes and resets PDF viewer state from Ghostscript imager state, including black/white colors and default line/text state.
- Writes high-level client colors through `pdf_reset_color`, supporting direct DeviceGray/RGB/CMYK operators, PDF color-space resources plus `scn`/`SCN`, colored/uncolored patterns, PatternType 2 shadings, and process-color fallback.
- Converts colorant strings to PDF COS names with `pdf_string_to_cos_name`.
- Serializes transfer maps, black generation, and undercolor removal into sampled PDF Functions, with identity detection and special signed-range handling for UCR.
- Recognizes many predefined spot halftone functions by resampling them against Ghostscript halftone orders; otherwise writes sampled spot functions.
- Writes spot, screen, colorscreen, threshold, threshold2, multiple, and multiple-colorscreen halftones as PDF halftone dictionaries or streams.
- Opens and finalizes ExtGState resources, substitutes duplicate resources, registers them in the page resource dictionary, and emits `/R... gs`.
- `pdf_prepare_drawing` updates common state for fill/stroke/image operations: transparency/blend/alpha, halftone, transfer, BG/UCR, halftone phase, overprint mode, smoothness, and text knockout.
- `pdf_prepare_fill`, `pdf_prepare_stroke`, `pdf_prepare_image`, and `pdf_prepare_imagemask` provide operation-specific wrappers, including fill/stroke overprint and stroke-adjust handling.

Notable dependencies:
- Ghostscript state/halftone/function APIs: `gsstate.h`, `gsfunc0.h`, `gxdht.h`, `gxht.h`, `gzht.h`, `gxfmap.h`, `gxdcolor.h`, and `gxpcolor.h`.
- PDF color-space and pattern helpers from `gdevpdfg.h`, `gdevpdfx.h`, and `gdevpdfo.h`.
- Stream compression support from `szlibx.h` for sampled function streams.

Research notes:
- The file is largely a state-delta engine: it avoids re-emitting color and graphics-state commands when saved IDs and saved high-level colors match current viewer state.
- Transparency is only emitted for PDF 1.4+; earlier compatibility levels return rangecheck when alpha, masks, or transparency stack state cannot be represented.
- PDF/X suppresses some preservation paths such as halftone/transfer emission.
- The `pdf_open_gstate` interrupt convention is used to request stream-context changes before writing `gs` commands.
