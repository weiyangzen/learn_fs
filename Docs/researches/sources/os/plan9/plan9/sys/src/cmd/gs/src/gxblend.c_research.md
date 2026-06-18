# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxblend.c

Purpose: Implements PDF transparency blend and compositing functions for 8-bit and 16-bit channels.

Key entry points:
- `art_blend_pixel_8()` computes separable and selected non-separable blend modes for 8-bit pixels.
- `art_blend_pixel()` computes similar blend modes for 16-bit `ArtPixMaxDepth`.
- `art_pdf_union_8()` and `art_pdf_union_mul_8()` combine alpha values.
- `art_pdf_composite_pixel_alpha_8()` composites source-over with optional blend mode.
- `art_pdf_uncomposite_group_8()`, `art_pdf_recomposite_group_8()`, and `art_pdf_composite_group_8()` handle group uncompositing/recompositing.
- `art_pdf_composite_knockout_simple_8()`, `art_pdf_composite_knockout_isolated_8()`, and `art_pdf_composite_knockout_8()` handle knockout transparency cases.

Important internals:
- `art_blend_luminosity_rgb_8()` and CMYK variant implement luminosity behavior with clipping back into gamut.
- `art_blend_saturation_rgb_8()` and CMYK variant implement saturation behavior.
- Lookup tables `art_blend_sq_diff_8` and `art_blend_soft_light_8` support SoftLight.

Behavior:
- Implements Normal, Compatible-as-Normal, Multiply, Screen, Overlay, SoftLight for 8-bit, HardLight, ColorDodge, ColorBurn, Darken, Lighten, Difference, Exclusion, Luminosity, Color, Saturation, and Hue.
- For CMYK non-separable modes, comments state components are already complemented.
- DeviceGray Hue/Saturation/Color/Luminosity emit debug messages and do not implement meaningful transforms.
- Group operations use PDF alpha union math and 8-bit fixed-style rounding.

Dependencies:
- Depends on `gxblend.h`, `gstparam.h`, Ghostscript debug printing, `bits32`, and blend-mode enums.

Notable risks:
- In `art_blend_pixel()` the 16-bit `BLEND_MODE_ColorBurn` case falls through into `BLEND_MODE_Darken` because there is no `break`.
- Some 32-bit copy idioms rely on caller-guaranteed padding/alignment from `gxblend.h`.
- The disabled `art_pdf_composite_pixel_knockout_8()` block contains unfinished/reference code and is not compiled.
