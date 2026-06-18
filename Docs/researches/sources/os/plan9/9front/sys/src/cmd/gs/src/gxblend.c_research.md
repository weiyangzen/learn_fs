# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxblend.c

Implements reference PDF 1.4/1.5 blend and transparency compositing routines for 8-bit and 16-bit channel data.

Key behavior:
- Implements 8-bit blend modes: Normal/Compatible, Multiply, Screen, Overlay, SoftLight, HardLight, ColorDodge, ColorBurn, Darken, Lighten, Difference, Exclusion, Luminosity, Color, Saturation, and Hue.
- Provides RGB luminosity/saturation helpers with luminance-preserving gamut clipping and CMYK variants that operate on complemented CMY values while treating K specially.
- Provides 16-bit `ArtPixMaxDepth` blending for a subset of blend modes.
- Uses lookup tables for SoftLight support and squared-difference terms.
- Implements alpha union helpers for plain and mask-scaled alpha.
- Implements source-over alpha compositing with optional blending in `art_pdf_composite_pixel_alpha_8`.
- Implements group uncompositing/recompositing for non-isolated transparency groups.
- Implements isolated group compositing with optional group alpha tracking.
- Implements simple, isolated, and general knockout compositing paths, including shape/alpha-mask handling.

Dependencies:
- Uses Ghostscript blend-mode enum definitions from included parameter/state headers and the public prototypes in `gxblend.h`.
- Uses 32-bit arithmetic for scaled 8-bit compositing and assumes aligned pixel buffers in several copy fast paths.

Research notes:
- This is explicitly a reference implementation, not a high-performance pixel pipeline.
- Compatible blend mode is treated as Normal.
- DeviceGray Hue/Saturation/Color/Luminosity 8-bit cases only log that they are not implemented.
- The 16-bit `BLEND_MODE_ColorBurn` case lacks a `break` before `BLEND_MODE_Darken`, so it falls through into Darken behavior.
- Some knockout/compositing comments flag missing optimization and possible clamp concerns.
