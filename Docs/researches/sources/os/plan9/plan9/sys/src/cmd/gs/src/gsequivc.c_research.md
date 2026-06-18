# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsequivc.c

## Role

`gsequivc.c` computes equivalent CMYK process colors for spot/separation colorants by forcing Separation/DeviceN tint transforms through their alternate color spaces and capturing the resulting process color.

## Workflow

`update_spot_equivalent_cmyk_colors` checks the current graphics-state color space. For Separation or DeviceN spaces, it compares colorant names against device separation names that lack known equivalent CMYK values.

For a matching Separation it builds a temporary color with tint 1.0 and sets `use_alt_cspace`. For DeviceN it first rejects any component named `None`, then builds a zeroed client color with the matching component set to 1.0.

## Capture Mechanism

The file defines a temporary `color_capture_device` and replacement color-map procedures. The temp imager state uses `cmap_capture_cmyk_color`, and the temp device carries the separation index plus destination equivalent-color params.

Capture procs save CMYK directly, convert gray to K-only CMYK, or convert RGB to CMYK via `color_rgb_to_cmyk`. Separation/DeviceN capture procs should not execute because alternate color-space use is forced.

## Dependencies

Uses printer/deviceN structures, color conversion, color spaces, graphics state, and device params. Header contract is in `gsequivc.h`.

## Risks

The logic intentionally skips DeviceN spaces containing `None` because equivalent values would require color data not available at installation time. The final remap call ignores its return code, so failed tint transforms may leave equivalent color data unset without direct propagation.
