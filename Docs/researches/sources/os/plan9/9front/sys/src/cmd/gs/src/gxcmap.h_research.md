# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcmap.h

Internal interface for Ghostscript color mapping procedures.

Key contents:
- Defines procedure signatures for mapping gray, RGB, CMYK, RGB-alpha, Separation, and DeviceN concrete colors to `gx_device_color`.
- Defines device color-space-to-color-model mapping procs for gray/RGB/CMYK inputs.
- Defines `gx_cm_color_map_procs` for device-provided color-model conversion hooks.
- Defines `gx_color_map_procs` for imager-state color remapping hooks and halftone-status testing.
- Declares `gx_get_cmap_procs`, `gx_default_get_cmap_procs`, and `gx_set_cmap_procs`.
- Provides macros for invoking concrete color remappers through the current imager-state procedure table.
- Declares default conversions, color-component-index routines, color-mapping-proc routines, encode/decode routines, grayscale encoders, and the `unit_frac` clamp/convert macro.
- Defines component-name type constants, including ordinary names and separation names.

Notable dependencies:
- `gscsel.h`, `gxfmap.h`, `gxcindex.h`, and `gxcvalue.h`.

Research notes:
- This header separates two layers: color space to device color model, and final device color rendering/halftoning.
- Device methods can override color-model conversions while retaining generic rendering logic from `gxcmap.c`.
