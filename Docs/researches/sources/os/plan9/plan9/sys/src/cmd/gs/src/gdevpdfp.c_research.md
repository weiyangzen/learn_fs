# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfp.c

## Purpose

`gdevpdfp.c` implements get/put parameter handling for Ghostscript's PDF-writing device. It exposes real pdfwrite parameters, accepts write-only pseudo-parameters for `pdfmark` and DSC comments, enforces selected Distiller compatibility constraints, updates version/capability flags, and maps DSC metadata into PDF structures.

This is PDF device parameter plumbing, not filesystem code.

## Main Entry Points

- `gdev_pdf_get_params(gx_device *dev, gs_param_list *plist)`: writes current pdfwrite parameters to a parameter list, including `CoreDistVersion`, `CompatibilityLevel`, `.EmbedFontObjects`, `pdfmark`, `DSC`, and items from `pdf_param_items`.
- `gdev_pdf_put_params(gx_device *dev, gs_param_list *plist)`: reads/validates pdfwrite parameters or dispatches pseudo-parameters.
- `pdf_dsc_process(gx_device_pdf *pdev, const gs_param_string_array *pma)`: maps recognized DSC comments to PDF document/page state.

## Parameter Table

`pdf_param_items` maps many `gx_device_pdf` fields to parameter names, including:

- Distiller-style controls:
  - `PDFEndPage`
  - `PDFStartPage`
  - `Optimize`
  - `ParseDSCCommentsForDocInfo`
  - `ParseDSCComments`
  - `EmitDSCWarnings`
  - `CreateJobTicket`
  - `PreserveEPSInfo`
  - `AutoPositionEPSFiles`
  - `PreserveCopyPage`
  - `UsePrologue`
  - `OffOptimizations`
- Ghostscript-specific behavior:
  - `ReAssignCharacters`
  - `ReEncodeCharacters`
  - `FirstObjectNumber`
  - `CompressFonts`
  - `PrintStatistics`
  - `MaxInlineImageSize`
- Encryption:
  - `OwnerPassword`
  - `UserPassword`
  - `KeyLength`
  - `Permissions`
  - `EncryptionR`
  - `NoEncrypt`
- Viewer/OPDF/PDFX capabilities:
  - `ForOPDFRead`
  - `PatternImagemask`
  - `MaxClipPathSize`
  - `MaxShadingBitmapSize`
  - `MaxViewerMemorySize`
  - `HaveTrueTypes`
  - `HaveCIDSystem`
  - `HaveTransparency`
  - `OPDFReadProcsetPath`
  - `CompressEntireFile`
  - `PDFX`

## Pseudo-Parameter Flow

- If `pdfmark` is present:
  - `pdf_open_document` is called.
  - `pdfmark_process` handles the mark array.
  - Errors are signaled on the `pdfmark` parameter.
- If `DSC` is present:
  - `pdf_open_document` is called.
  - `pdf_dsc_process` handles DSC key/value pairs.
  - Errors are signaled on `DSC`.
- Real parameter validation is skipped for these pseudo-parameter-only calls.

## Real Parameter Handling

- Honors `LockDistillerParams`: if already locked and not being unlocked, most PDF-specific reset attempts are ignored.
- Enforces:
  - `.EmbedFontObjects == 1`
  - `CoreDistVersion == 5000`
  - `CompatibilityLevel` rounded/substituted to supported values.
  - `FirstObjectNumber` can only change before object IDs have advanced, or to the same value.
- Handles `ProcessColorModel` early because lower-level device parameter handling depends on it.
- Updates capability flags for `PDFX` and `ForOPDFRead`.
- Adjusts `pdev->version` based on compatibility and TrueType support.
- Reduces device resolution if page device dimensions exceed Acrobat coordinate limits.
- On failure, restores saved PDF-specific fields and color state.

## DSC Processing

Recognized DSC keys include:

- Document info:
  - `Creator` to `/Creator`
  - `Title` to `/Title`
  - `For` to `/Author`
- Orientation:
  - `Orientation`
  - `PageOrientation`
- Viewing orientation:
  - `ViewingOrientation`
  - `PageViewingOrientation`
- EPS and bounding boxes:
  - `EPSF`
  - `BoundingBox`
  - `PageBoundingBox`

DSC info is ignored entirely when `ParseDSCComments` is false. Creator/title/author are only written when `ParseDSCCommentsForDocInfo` or `PreserveEPSInfo` is enabled.

## Risks and Edge Cases

- The comment block lists many Distiller parameters/features that are incomplete or deferred.
- `pdf_dsc_process` parses with `sscanf` and silently continues on malformed bounding boxes/orientations.
- Compatibility coercion may surprise callers because unsupported values are rounded to nearby supported levels.
- Failure restoration copies fields by parameter-table offsets; fields outside that table are restored manually or may remain changed if not handled.
- `save_dev.saved_stroke_color` restoration appears to assign from `save_dev.saved_fill_color`, which is suspicious and worth review if this code is maintained.
