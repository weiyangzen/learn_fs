# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jquant1.c

This is the Independent JPEG Group one-pass color quantizer, compiled only when `QUANT_1PASS_SUPPORTED` is enabled. It implements fast indexed-color output by creating an orthogonal, preselected colormap before seeing image pixels.

The module chooses per-component color counts from `cinfo->desired_number_of_colors`, biased for RGB by trying green, then red, then blue. `create_colormap()` builds all component-value combinations, while `create_colorindex()` precomputes pixel-value-to-colormap-index contributions so row conversion is mostly table lookup and addition.

It supports three output modes: no dithering, ordered dithering with a 16x16 Bayer matrix, and Floyd-Steinberg dithering. There are specialized 3-component fast paths for no dithering and ordered dithering, plus general paths for other component counts up to `MAX_Q_COMPS` 4.

Floyd-Steinberg state is stored as per-component error arrays allocated through libjpeg's memory manager. Rows alternate left-to-right and right-to-left, using the standard 7/16, 3/16, 5/16, 1/16 distribution. Ordered dithering pads the color index table so dithered values outside `0..MAXJSAMPLE` clamp via table lookup.

Integration points are the `jpeg_color_quantizer` methods installed by `jinit_1pass_quantizer()`: `start_pass`, `finish_pass`, `new_color_map`, and the selected `color_quantize` callback. The code depends on `jinclude.h`, `jpeglib.h`, libjpeg memory pools, error macros, `sample_range_limit`, and the decompressor fields for output size, color space, dithering mode, and colormap reporting.

Important constraints: external colormap switching is rejected with `JERR_MODE_CHANGE`; requested colors must fit in `JSAMPLE`; component count over four is rejected; and ordered dither table creation is lazy. This is performance-oriented image code, not filesystem logic, but it is part of the Plan 9 source snapshot through Ghostscript's vendored JPEG library.
