# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevjpeg.c

## Role
`gdevjpeg.c` implements Ghostscript JPEG output devices: `jpeg`, `jpeggray`, and `jpegcmyk`.

## Device Definitions
- `gx_device_jpeg` extends a printer device with `JPEGQ` and `QFactor` quality settings.
- `gs_jpeg_device`: 24-bit RGB.
- `gs_jpeggray_device`: 8-bit grayscale.
- `gs_jpegcmyk_device`: 32-bit CMYK with custom CMYK mapping.

## Parameters
- `jpeg_get_params` exposes `JPEGQ` and `QFactor`.
- `jpeg_put_params` validates `JPEGQ` in 0..100 and `QFactor` in 0..1e6, delegates standard printer params, then stores values.
- `JPEGQ` takes precedence over `QFactor` in compression setup.

## Color Mapping
- `jpegcmyk_map_cmyk_color` inverts CMYK bytes when packing a color index, matching expectations of Photoshop and other CMYK JPEG consumers.
- `jpegcmyk_map_color_rgb` approximates RGB from inverted CMYK values.

## Print Path
- `jpeg_print_page` allocates a scanline buffer, IJG/Ghostscript JPEG compression state, output stream buffer, and input filter buffer.
- Configures DCTEncode defaults, disables Ghostscript quality adjustment (`QFactor = 1.0` in state), lets IJG emit markers, and sets density from device resolution.
- Selects IJG input color space based on device depth: CMYK, RGB, or grayscale.
- Applies `JPEGQ` or linear quality based on `QFactor`.
- Feeds every scanline from the Ghostscript printer buffer into a DCT filter stream and flushes the file stream at the end.

## Risks and Notes
- Sequential file/image encoder only; no filesystem metadata logic.
- Carefully frees buffers and destroys JPEG state on normal/error paths.
