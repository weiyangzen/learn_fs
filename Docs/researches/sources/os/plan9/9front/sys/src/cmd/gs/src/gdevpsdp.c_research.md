# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdp.c

## Purpose
Implements Distiller-style parameter get/put handling for PostScript and PDF writers.

## Key Behavior
- Defines accepted filter names and version constraints for color/gray/mono images.
- Maps parameter names to `psdf_distiller_params` and `psdf_image_params` fields.
- Writes current parameter values for:
  - general encoding/compression settings,
  - color conversion strategy and calibration profile strings,
  - color/gray/mono image processing options,
  - font embedding lists and policies.
- Reads and validates incoming parameters:
  - enum names,
  - booleans/ints/floats,
  - image dictionaries,
  - image filter names,
  - profile strings,
  - incremental font embedding arrays.
- Validates image dicts immediately by allocating matching stream states and applying filter-specific parameter readers.
- Implements special `AlwaysEmbed`/`NeverEmbed` semantics with incremental add/delete and complete-list replacement variants.
- Honors `LockDistillerParams` by ignoring psdf-specific updates while still allowing normal device parameters.

## Dependencies
Uses Ghostscript parameter list APIs, stream filter parameter readers, JPEG/DCT, CCITT Fax, LZW, RunLength, Flate/zlib, and vector device parameter handling.

## Research Notes
This file owns psdf parameter persistence and validation. It is important because `gdevpsdi.c` assumes stored filter templates and dictionaries are already coherent.
