# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsequivc.c

This file computes equivalent CMYK colors for spot colorants in Separation and DeviceN color spaces.

Purpose:
- Devices with spot colors may need process-color approximations for display or output metadata.
- The code uses tint transform functions to derive CMYK equivalents for spot colorants not directly present in the process model.

Workflow:
- `update_spot_equivalent_cmyk_colors` checks the current graphics-state color space.
- For Separation spaces, it matches the separation name against device separations needing CMYK equivalents.
- For DeviceN spaces, it scans component names, skipping spaces containing `None` because alternate-color information can be encoded in the color value rather than the color space.
- It copies the color space, forces `use_alt_cspace`, builds a color with the target spot at 100%, and remaps it through custom capture color-mapping procedures.
- Capture procedures convert gray/RGB/CMYK mappings into saved CMYK fractions.

Important structures:
- A temporary `color_capture_device` carries the target separation index and output `equivalent_cmyk_color_params`.
- A temporary imager state replaces `cmap_procs` with capture procs and forces alternate color-space use.

Supported capture inputs:
- Gray maps to K-only CMYK.
- RGB converts through `color_rgb_to_cmyk`.
- CMYK is saved directly.
- Separation/DeviceN capture callbacks should not execute and only debug-print if reached.

Integration examples in comments reference PSD, display, and tiffsep-style devices.
