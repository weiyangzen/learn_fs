# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtsep.c

Implements uncompressed TIFF grayscale, CMYK, and separation-output devices: `tiffgray`, `tiff32nc`, and `tiffsep`.

Key behavior:
- `tiffgray` is an 8-bit grayscale printer device that writes uncompressed min-is-black TIFF data through the shared TIFF writer.
- `tiff32nc` is a 32-bit CMYK printer device using separated 8-bit-per-plane CMYK color mapping and uncompressed TIFF output with `Photometric_separated`.
- Defines sorted TIFF directory templates and bits-per-sample indirect values for grayscale and CMYK output.
- Defines `tiffsep_device`, a DeviceN-capable printer with TIFF state for one composite CMYK output plus per-separation TIFF states/files, `gs_devn_params`, and equivalent CMYK color parameters for spot colors.
- Provides GC enumeration/relocation for dynamically stored separation-name data.
- Builds an extended device-procedure table supporting DeviceN component lookup, encode/decode, color mapping procs, and spot equivalent-color updates.
- Maps gray/RGB/CMYK source color spaces into DeviceN component arrays using separation-order maps.
- Encodes color components into `gx_color_index` with configurable bits per component and decodes them back in reverse component order.
- Gets/puts DeviceN printer parameters through the shared `devn_*` helpers, allowing separation names/order and spot equivalent data.
- Creates output separation file names by appending the standard colorant name or generated `sN` spot name plus `.tif` to the base output name; raw separation-name escaping is noted but disabled.
- Determines how many separations to output from device component limits, standard CMYK components, requested `SeparationOrder`, and spot-color count.
- Builds component-to-separation maps and CMYK-equivalent maps for process and spot colors.
- `tiffsep_print_page` writes a composite CMYK TIFF page, opens/reuses per-separation grayscale TIFF files, writes one grayscale separation file per selected component, builds a CMYK-equivalent raster line, then finalizes all strip/page metadata.
- `tiffsep_prn_close` closes any separation files left open across pages.

Dependencies:
- Uses `gdevprn.h`, `gdevtifs.h`, `gdevdevn.h`, and `gsequivc.h`.
- Depends on DeviceN/separation helpers, equivalent CMYK color updates, Ghostscript printer raster access, and the shared TIFF writer.

Research notes:
- `tiffsep` can accept more spot colors than it can image in one pass; users can use `SeparationOrder` across multiple passes to emit more than the component limit.
- Separation file naming deliberately avoids raw spot names by default because operating systems restrict filename characters.
