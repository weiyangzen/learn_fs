# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtsep.c

## Purpose
Implements uncompressed TIFF output devices for grayscale, CMYK, and separations: `tiffgray`, `tiff32nc`, and `tiffsep`.

## Main Concepts
- `tiffgray` writes 8-bit grayscale TIFF.
- `tiff32nc` writes 32-bit uncompressed CMYK TIFF.
- `tiffsep` writes a composite CMYK-equivalent TIFF plus separate 8-bit grayscale TIFF files for each selected process/spot separation.
- `tiffsep_device` embeds DeviceN parameters, equivalent CMYK spot-color metadata, one TIFF state for the composite file, TIFF states for each separation, and sidecar `FILE *` handles.

## Key Functions
- `tiffgray_print_page`, `tiff32nc_print_page`: shared pattern of writing a TIFF directory, streaming rows, ending strip/page, and freeing line buffers.
- DeviceN mapping:
  - `tiffsep_get_color_mapping_procs`
  - `tiffsep_get_color_comp_index`
  - `tiffsep_encode_color`
  - `tiffsep_decode_color`
  - `tiffsep_update_spot_equivalent_colors`
- Parameter handling:
  - `tiffsep_get_params`
  - `tiffsep_put_params`
- Separation file handling:
  - `create_separation_file_name`
  - `copy_separation_name`
  - `tiffsep_prn_open`
  - `tiffsep_prn_close`
- Raster composition:
  - `number_output_separations`
  - `build_comp_to_sep_map`
  - `build_cmyk_map`
  - `build_cmyk_raster_line`
  - `tiffsep_print_page`

## Behavior
- Supports more spot colors than can be imaged in one pass, relying on `SeparationOrder` for multi-pass output.
- Separation filenames are derived from the main output filename plus `.Cyan.tif`, `.Magenta.tif`, `.Yellow.tif`, `.Black.tif`, or `.sN.tif` for spot color indexes.
- Individual separation files store inverted component values because TIFF grayscale is additive while separations are subtractive.
- Composite CMYK data is built from process colors and equivalent CMYK values for spots.

## Notable Risks
- Separation-name escaping is explicitly not implemented; the safer numeric spot suffix path is used.
- `map_comp_to_sep` is not initialized before selective assignment, so unexpected component maps could read stale stack values.
- `gx_parse_output_file_name` return code is overwritten/ignored except for its format pointer effect.
- Several output and TIFF-finalization errors are not checked.
- Sidecar files can remain open across pages unless page-number formatting requires per-page files.

## Filesystem Relevance
Creates and writes multiple TIFF output files derived from the output filename. It is image/printer output code, not filesystem implementation logic.
