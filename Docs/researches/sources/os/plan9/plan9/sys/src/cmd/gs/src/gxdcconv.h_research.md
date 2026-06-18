# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcconv.h

Internal Ghostscript device color conversion interface.

- Declares `frac`-based conversion helpers between RGB, CMYK, and gray:
  - `color_rgb_to_gray`
  - `color_rgb_to_cmyk`
  - `color_cmyk_to_gray`
  - `color_cmyk_to_rgb`
- All routines accept `const gs_imager_state *pis`, so conversions can account for imager-state color behavior rather than being pure numeric transforms.
- Includes only `gxfrac.h`; relies on prior visibility of `gs_imager_state`.

Role in subsystem: small internal API boundary used by device/color rendering code that needs canonical fractional color-space conversions.
