# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfg.c

Ghostscript `pdfwrite` graphics-state management. It tracks the PDF viewer state implied by emitted content and writes only the needed color and ExtGState changes.

Key behavior:
- Saves/restores viewer graphics state in `pdev->vgstack`, including transfers, alpha, blend mode, halftones, BG/UCR, overprint, smoothness, text knockout, stroke adjustment, colors, line parameters, and dash data.
- Initializes/reset viewer state from Ghostscript imager state and default black colors.
- Writes colors through DeviceGray/RGB/CMYK operators, resource color spaces with `scn`/`SCN`, colored/uncolored patterns, PatternType 2 shadings, or process-color fallback.
- Converts colorant strings into COS names.
- Serializes transfer maps, black generation, and undercolor removal into sampled PDF Functions.
- Recognizes many predefined spot halftone functions; otherwise emits sampled spot functions.
- Writes spot, screen, colorscreen, threshold, threshold2, multiple, and multiple-colorscreen halftones.
- Creates, deduplicates, registers, and emits ExtGState resources with `/R... gs`.
- `pdf_prepare_drawing` updates transparency, alpha, blend mode, halftone, transfer, BG/UCR, halftone phase, overprint mode, smoothness, and text knockout.
- Fill/stroke/image/imagemask wrappers add operation-specific overprint, stroke adjustment, and fill color handling.

Research notes:
- The file is mainly a state-delta engine that avoids re-emitting unchanged graphics-state commands.
- Transparency requires PDF 1.4+; older compatibility levels return `rangecheck` for unrepresentable alpha/mask/transparency stack state.
- PDF/X suppresses some preservation paths such as halftone and transfer emission.
