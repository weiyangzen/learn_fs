# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevndi.c

This file implements DeviceN halftone rendering helpers. It converts fractional process-color components into Ghostscript device colors, choosing between pure encoded colors, colored halftones, binary halftones, and WTS device colors.

The file defines fractional lookup tables `q0` through `q7` and exports `fc_color_quo`, used by the fractional color macro in `gzht.h` for fast conversion of small denominators.

`gx_render_device_DeviceN_wts` is the WTS-specific constructor. It initializes a WTS device color, stores the halftone pointer, copies fractional levels, and builds a `plane_vector` by encoding one-max-component colors through the device's `encode_color` procedure. For non-separable/non-linear encodings it also samples the zero-vector case for monochrome inversion.

`gx_render_device_DeviceN` is the main DeviceN renderer. It computes per-component maximum dither values from `dev->color_info`, converts each fractional input into an integer base color and halftone level, and tracks whether dithering is needed. If no component needs dithering, it encodes and returns a pure color. Otherwise it sets per-component colored-halftone state, completes the halftone with `gx_complete_halftone`, applies halftone phase modulo the halftone LCM dimensions, and reduces single-plane cases.

`gx_devn_reduce_colored_halftone` handles colored halftones with zero or one active varying component. Zero active planes become a pure color. One active plane becomes a binary halftone with a base and next color; subtractive devices invert both level and color pair to account for additive halftone orders.

Filesystem relevance: none. This is raster color/halftone rendering code.
