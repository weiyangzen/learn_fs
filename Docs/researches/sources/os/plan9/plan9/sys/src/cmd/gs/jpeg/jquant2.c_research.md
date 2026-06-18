# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jquant2.c

This is the IJG two-pass color quantizer, compiled when `QUANT_2PASS_SUPPORTED` is enabled. It selects an image-specific colormap during a prescan and then maps pixels to that colormap, optionally with Floyd-Steinberg dithering.

The first pass builds a reduced-precision RGB histogram: 5 bits for component 0, 6 for component 1, and 5 for component 2. Histogram cells are `UINT16`, with overflow clamped. The code is hard-wired to three output color components and uses scaled distance weights of 2 for red, 3 for green, and 1 for blue, respecting the configured RGB order.

Color selection follows a Heckbert-style median-cut workflow. It starts with one box covering the used color space, shrinks boxes to nonzero histogram cells, splits by population for the first half of the requested colors and by scaled volume after that, then computes a pixel-count-weighted mean color for each final box.

The second pass reuses the histogram as an inverse colormap cache. Empty cache cells trigger `fill_inverse_cmap()`, which fills a small histogram subbox by selecting nearby colormap candidates and using incremental squared-distance calculations to choose nearest colors. This avoids full colormap searches for every pixel.

Dithering support is limited to none or Floyd-Steinberg; requested ordered dither is coerced to F-S. The F-S path uses one row of three-component error storage, alternates scan direction by row, applies an error limiter table to reduce artifacts, clamps through `sample_range_limit`, then emits cached nearest-colormap indexes.

`jinit_2pass_quantizer()` allocates the quantizer object, histogram rows, optional saved colormap, and optional F-S workspace. `start_pass_2_quant()` switches between prescan and output pass behavior, validates color counts, zeroes histogram/cache state when needed, and handles external colormap remapping via `new_color_map_2_quant()`.

Key constraints: only 3-component output is implemented; desired colors must be between 8 and `MAXJSAMPLE+1` for self-generated maps; external maps must have 1 to `MAXNUMCOLORS` colors; and the algorithm is memory-conscious for old segmented-memory systems. This is image quantization infrastructure within the vendored JPEG library.
