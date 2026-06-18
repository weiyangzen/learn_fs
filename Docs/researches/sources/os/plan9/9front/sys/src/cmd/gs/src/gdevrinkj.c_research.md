# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevrinkj.c

Ghostscript printer device bridge for the `rinkj` “resplendent inkjet” stack, targeting high-resolution inkjet output through Rinkj screening and Epson 870 output modules.

Key behavior:
- Defines the public `rinkj` printer device at 720x720 DPI by default, with a DeviceN-capable color model and default CMYK process colorants.
- Supports process color models `DeviceGray`, `DeviceRGB`, `DeviceCMYK`, and `DeviceN`, with dynamic separation color names.
- Implements Ghostscript color mapping hooks: color-space-to-device component mapping, component index lookup, `encode_color`, `decode_color`, and limited reverse RGB mapping.
- Exposes and accepts parameters including `ProcessColorModel`, `SeparationColorNames`, `ProfileOut`, and `SetupFile`; also emits `CRDDefault` via `sample_device_crd_get_params`.
- Optionally opens an ICC output profile with the bundled ICC API and uses the profile lookup object to transform RGB or CMYK scanlines to CMYK.
- Parses a setup/config file for `AddLut`, `Dither`, `Aspect`, and printer-specific settings, then installs LUTs into the Rinkj screening device.
- Initializes a Rinkj pipeline: file byte stream -> Epson 870 device -> error-buffered screen device.
- Converts Ghostscript page raster data into planar CMYK data, then duplicates planes into a seven-plane output layout `CMYKcmk`.
- Contains a color-conversion cache for ICC lookup results.

Notable dependencies:
- Ghostscript printer and parameter APIs: `gdevprn.h`, `gsparam.h`, `gscrd.h`, `gscrdp.h`, `gdevdcrd.h`, `gxdcconv.h`.
- ICC support from `icc.h`.
- Rinkj private modules: `rinkj-device.h`, `rinkj-byte-stream.h`, `rinkj-screen-eb.h`, and `rinkj-epson870.h`.

Research notes:
- This is printer/output rendering infrastructure, not filesystem code.
- DeviceN support is partial: several comments note `SeparationOrder` is not yet honored.
- `SetupFile` appears operationally important: `rinkj_set_luts` calls `fopen` and then uses the resulting `FILE *` without a null check.
- In the RGB and 5-plane ICC paths, `hash` is computed from `color` before `color` is assigned; that is an uninitialized-read bug in the color cache path.
- `rinkj_write_image_data` allocates four `plane_data` buffers but frees using `n_planes_in`; unusual color-component counts could make cleanup unsafe.
