# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfp.c

Ghostscript `pdfwrite` parameter get/put implementation. It exposes PDF device parameters, handles write-only `pdfmark` and `DSC` pseudo-parameters, updates compatibility/device settings, and maps selected DSC comments into PDF metadata/page state.

Key behavior:
- Defines supported PDF-specific parameter items, including Distiller-compatible controls, Ghostscript-specific toggles, encryption fields, OPDF-read behavior, clipping/shading/viewer limits, and PDF/X.
- `gdev_pdf_get_params` writes inherited PSDF parameters plus PDF-specific values such as `.EmbedFontObjects`, `CoreDistVersion`, `CompatibilityLevel`, `pdfmark`, and `DSC`.
- `gdev_pdf_put_params` handles pseudo-parameters first:
  - `pdfmark` opens the document and dispatches to `pdfmark_process`.
  - `DSC` opens the document and dispatches to `pdf_dsc_process`.
- Enforces `LockDistillerParams` by ignoring PDF-specific reset attempts unless unlocking.
- Validates `.EmbedFontObjects` and `CoreDistVersion`.
- Normalizes requested `CompatibilityLevel` to supported PDF levels and adjusts version handling for PDF/X and OPDF-read mode.
- Reads `ProcessColorModel`, updates the PDF process color model, and resets initial fill/stroke colors.
- Validates `FirstObjectNumber`, only allowing changes before object allocation or to the existing effective value.
- Adjusts resolution if page dimensions would exceed Acrobat’s user-coordinate limits.
- Restores saved device state on parameter errors.
- `pdf_dsc_process` recognizes DSC comments for creator/title/author, orientation, viewing orientation, EPS state, and bounding boxes.

Notable dependencies:
- Generic PSDF parameter handling from `gdev_psdf_get_params` and `gdev_psdf_put_params`.
- `pdfmark_process`, `pdf_open_document`, COS dictionary helpers, and page/DSC state fields in `gx_device_pdf`.

Research notes:
- The comments list many Distiller parameters and features that are partially implemented or not implemented.
- OPDF-read mode forces resources-before-usage behavior, disables CFF/PDF widths/stroke color support, sets PDF 1.2-like behavior, and permits large inline images to reduce temporary buffering.
- PDF/X forces compatibility behavior toward PDF 1.3.
- This file configures PDF output behavior; it does not implement filesystem logic.
