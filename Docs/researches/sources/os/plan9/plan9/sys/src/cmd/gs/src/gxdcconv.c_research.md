# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcconv.c

## Purpose
Implements color conversion between Ghostscript device color spaces, specifically RGB-to-gray, RGB-to-CMYK, CMYK-to-gray, and CMYK-to-RGB.

## Public Surface
- `color_rgb_to_gray(frac r, frac g, frac b, const gs_imager_state *pis)`.
- `color_rgb_to_cmyk(frac r, frac g, frac b, const gs_imager_state *pis, frac cmyk[4])`.
- `color_cmyk_to_gray(frac c, frac m, frac y, frac k, const gs_imager_state *pis)`.
- `color_cmyk_to_rgb(frac c, frac m, frac y, frac k, const gs_imager_state *pis, frac rgb[3])`.

## Implementation
- RGB to gray uses luminance weights.
- RGB to CMYK computes subtractive complements, derives black from the minimum of C/M/Y, applies black-generation and undercolor-removal transfer maps from the imager state when available, and otherwise uses fallback defaults.
- CMYK to gray maps CMY to weighted non-gray plus black, clamping to black when the sum exceeds full scale.
- CMYK to RGB uses Adobe-compatible formulas controlled by `USE_ADOBE_CMYK_RGB`, with fast cases for no black and full black.

## Dependencies
Uses fractional arithmetic, luminance constants, imager transfer maps, and debug tracing.

## Risks and Notes
- The source explicitly notes alternate non-Adobe formulas that produced better display results, but this build selects Adobe-compatible behavior.
- RGB to CMYK depends on black-generation and undercolor-removal maps matching PostScript initialization behavior when an imager state is present.

Filesystem relevance: none. This is color conversion math.
