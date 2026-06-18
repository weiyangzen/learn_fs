# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcmap.c

## Purpose
Implements Ghostscript color mapping: device color encode/decode defaults, color-space-to-device-color-model conversions, component name lookup, color remapping into direct or halftoned device colors, transfer-map support, and legacy map_rgb/map_color helpers.

## Public Surface
- Device color packing: `gx_default_encode_color`, `gx_default_decode_color`, error encode/decode procedures, gray encode helpers, and backward-compatible gray encoding.
- Color-model mapping procedure providers for DeviceGray, DeviceRGB, DeviceCMYK, and DeviceRGBK.
- Component lookup procedures for Gray/RGB/CMYK/RGBK devices.
- Cmap procedure selection: `gx_get_cmap_procs`, `gx_default_get_cmap_procs`, `gx_set_cmap_procs`.
- Standard color-space remappers/concretizers for DeviceGray, DeviceRGB, and DeviceCMYK.
- Transfer helpers: `gs_identity_transfer`, `gs_mapped_transfer`, `gx_set_identity_transfer`, optional interpolation map function.
- Legacy/default device color mappers for monochrome, grayscale, RGB, CMYK, and RGB-alpha APIs.

## Implementation
- For separable linear devices, encodes color indexes by shifting each component into the device-specified bit fields and decodes by scaling bit-field values back to `gx_color_value`.
- Provides default conversions among Gray, RGB, CMYK, and RGBK color models, including RGB to CMYK through black generation and undercolor removal when imager state is available.
- Chooses halftoned or direct color mapping procedures depending on `gx_device_must_halftone`.
- Direct mapping applies color model conversion, transfer functions, polarity handling, conversion to `gx_color_value`, then device `encode_color`; if direct encoding fails, it falls back to halftoned rendering.
- Halftoned mapping converts to device colorants, applies transfer/polarity handling, then calls `gx_render_device_DeviceN` and loads the resulting device color.
- DeviceN and Separation mapping use `gs_devicen_color_map` to place source components into device colorant order, with special handling for Separation All and additive-device inversion.
- DeviceGray/RGB alpha remappers use `map_rgb_alpha` only where applicable; CMYK alpha is explicitly ignored.

## Dependencies
Uses device color, imager state, transfer maps, halftone rendering, DeviceN colorant mapping, color conversion helpers from `gxdcconv.c`, luminance weights, and Ghostscript device procedure vectors.

## Risks and Notes
- Debug checks require separable-linear devices for the default encode/decode routines, but release behavior still assumes correct device metadata.
- `gx_error_decode_color` loops from `num_components` down to zero, which writes one past the usual last component index if the buffer is only `num_components` elements.
- CMYK alpha handling is marked ignored.
- RGB-to-CMYK fallback without imager state contains a suspicious `min(m, g)` term where yellow would be expected; the surrounding comment says this mode supports PCL RasterOp behavior.

Filesystem relevance: none. This is rendering color infrastructure.
