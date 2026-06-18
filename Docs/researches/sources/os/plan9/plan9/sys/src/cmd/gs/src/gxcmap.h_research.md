# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcmap.h

## Purpose
Declares the color mapping interfaces that connect Ghostscript color spaces and imager state to device color models and device color indexes.

## Public Surface
- Function-signature macros for concrete gray/RGB/CMYK/RGBA/Separation/DeviceN remapping.
- `gx_cm_color_map_procs`: maps standard color spaces into a device colorant vector.
- `gx_color_map_procs`: maps concrete color values into a `gx_device_color` and reports whether the mapping is halftoned.
- Procedure selection APIs: `gx_get_cmap_procs`, `gx_default_get_cmap_procs`, `gx_set_cmap_procs`.
- Remap macros: `gx_remap_concrete_gray`, `gx_remap_concrete_rgb`, `gx_remap_concrete_cmyk`, `gx_remap_concrete_rgb_alpha`, `gx_remap_concrete_separation`, `gx_remap_concrete_devicen`.
- Device procedure typedefs for color component lookup, color-model mapping procs, color encoding, and color decoding.
- Default procedure declarations for Gray/RGB/CMYK/RGBK devices and error handlers.

## Semantics
- Devices may provide custom color-space-to-color-model conversion procedures; otherwise standard conversions are used.
- Component name lookup distinguishes ordinary names from separations via `component_type`.
- The header includes `gxcindex.h` and `gxcvalue.h`, tying color mapping to both packed device color indexes and driver-interface component values.

## Dependencies
Requires Ghostscript device color structures, imager state, fractional color maps, color selection ids, and device procedure conventions.

## Risks and Notes
- Many macros dispatch through procedure pointers and assume `pis->cmap_procs` has been refreshed after device changes.
- The duplicated CMYK default declarations are harmless but redundant.

Filesystem relevance: none. This is a rendering interface header.
