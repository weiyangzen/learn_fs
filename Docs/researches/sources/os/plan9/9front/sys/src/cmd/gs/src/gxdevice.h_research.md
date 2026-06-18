# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevice.h

This header is the device-implementor companion to `gxdevcli.h`. It includes the client interface plus file-name, parameter, malloc, and stdio compatibility headers, then provides device initialization macros, default procedure declarations, forwarding procedure declarations, implementation utilities, clipping macros, and media parameter helpers.

The default page-size macros select U.S. Letter or A4 depending on `A4`. The `std_device_part*` and `std_device_*` macro families construct static device initializer bodies while insulating device templates from changes in `gx_device_common`. Variants cover open/closed prototypes, explicit color info, extended DeviceN-style color info, anti-aliasing, standard color-depth-derived models, and margin/offset variants.

The default procedure declarations cover optional device hooks and fallback implementations for mapping, drawing, parameter access, image handling, compositors, text, patterns, high-level color fills, linear-color shadings, and spot equivalent colors. It also declares standard color mapping procedures for black-on-white, white-on-black, grayscale, RGB, CMYK, and 8-bit gray.

Forwarding-device declarations mirror most device procedures, forwarding operations through `gx_device_forward.target`. The header also exposes helpers for filling in procedure tables, forwarding/copying color procedures, checking separable encodings, setting component masks/shifts, and copying color/page parameters from targets.

`gx_device_black`, `gx_device_white`, and inline cache-aware variants are declared here for implementors. Output-file helpers parse and open/close device output file names, including page-number formats.

The clipping macros `fit_fill*` and `fit_copy*` mutate rectangle/copy arguments to clip against device bounds and return early when empty. Copy clipping also adjusts source data pointers, source X offsets, raster-derived row offsets, and bitmap ids.

The media parameter section defines `gdev_input_media_t` and `gdev_output_media_t` plus routines to emit InputAttributes/OutputAttributes dictionaries.

Filesystem relevance: slight user-space file I/O relevance through output-file open/close helpers, but no filesystem implementation logic. Its main role is Ghostscript rendering-device implementation support.
