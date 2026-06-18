# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstext.h

## Purpose
Declares the driver-facing text interface: text source/operation flags, parameter structure, text begin/process/release APIs, return codes for client intervention, and glyph cache metric APIs.

## Public Surface
- Validation macros: `TEXT_HAS_MORE_THAN_ONE_`, `TEXT_OPERATION_IS_INVALID`, `TEXT_PARAMS_ARE_INVALID`.
- Source flags: `TEXT_FROM_STRING`, `TEXT_FROM_BYTES`, `TEXT_FROM_CHARS`, `TEXT_FROM_GLYPHS`, `TEXT_FROM_SINGLE_CHAR`, `TEXT_FROM_SINGLE_GLYPH`.
- Width flags: `TEXT_ADD_TO_ALL_WIDTHS`, `TEXT_ADD_TO_SPACE_WIDTH`, `TEXT_REPLACE_WIDTHS`.
- Result/action flags: `TEXT_DO_NONE`, `TEXT_DO_DRAW`, `TEXT_DO_CHARWIDTH`, false/true charpath and charboxpath flags.
- Other flags: `TEXT_INTERVENE`, `TEXT_RETURN_WIDTH`.
- `gs_text_params_t`: immutable input descriptor with source union, size, width adjustment fields, space char/glyph, replacement width arrays, and width array size.
- `dev_proc_text_begin` / `gx_device_text_begin`: device text-begin contract.
- Begin wrappers for PostScript text operators and generic `gs_text_begin`.
- Processing return codes: `TEXT_PROCESS_RENDER`, `TEXT_PROCESS_INTERVENE`, `TEXT_PROCESS_CDEVPROC`.
- Accessors, width queries, cache-control APIs, retry, and release.

## Semantics
- Exactly one `TEXT_FROM_*` and one `TEXT_DO_*` family member must be present.
- Single char/glyph sources must have `size == 1`.
- Additive width adjustment and replacement widths are mutually exclusive.
- `TEXT_PROCESS_RENDER` requires the client to render the current char/glyph and resume.
- `TEXT_PROCESS_INTERVENE` supports `kshow`/`cshow`-style between-character callbacks.
- `TEXT_PROCESS_CDEVPROC` asks the caller to execute CDevProc and feed results back through enumerator fields.

## Dependencies
Includes character-code and cache-device headers and forward-declares graphics state, device, imager, font, path, clip path, and device color types.

## Risks and Notes
- `widths_size` is marked probably unnecessary, suggesting historical API uncertainty.
- The operation mask is flexible, but only a constrained subset is valid; callers must use validation before relying on fields.
