# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdp.c

## Purpose
Implements get/put handling for shared Distiller-style PostScript/PDF parameters.

## Key Behavior
- Maps parameter names to `psdf_distiller_params` fields using `gs_param_item_t` tables.
- Defines supported image filter names and minimum psdf versions:
  - color/gray: DCT, Flate, LZW,
  - mono: CCITT Fax, Flate, LZW, RunLength.
- Writes current image parameters, image dictionaries, enum names, profile strings, and font embedding lists.
- Reads and validates image dictionaries immediately by allocating stream state and applying filter-specific parameter setters.
- Handles enum parameters such as `AutoRotatePages`, `Binding`, `DefaultRenderingIntent`, `ColorConversionStrategy`, `TransferFunctionInfo`, `UCRandBGInfo`, `DownsampleType`, and `CannotEmbedFontPolicy`.
- Implements incremental and complete update semantics for `AlwaysEmbed` and `NeverEmbed` using the public, deletion, and complete-list parameter names.
- Honors `LockDistillerParams` by ignoring psdf-specific updates while still allowing standard vector-device parameters.
- Clamps or normalizes image settings such as resolution, downsample threshold, and supported output depths.

## Dependencies
Uses Ghostscript parameter-list APIs, C parameter lists, DCT/CCITT validation hooks, stream templates, vector-device parameter handling, and psdf declarations.

## Research Notes
The top comment notes that `ColorConversionStrategy` behavior is largely not implemented. Parameter validation is stricter than runtime use in some places because dictionaries are checked by constructing actual stream states before accepting them.
