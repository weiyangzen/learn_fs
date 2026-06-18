# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxcf.c

Ghostscript printer-style export device for GIMP XCF files, with DeviceN/spot color support.

Key responsibilities:
- Defines `xcf_device`, extending printer-device state with color model, bits per component, process colorant names, separation names/order, and optional ICC profile lookup objects.
- Public devices: `xcf` default RGB plus spot support, and `xcfcmyk` default CMYK/DeviceN-oriented output.
- Color mapping procs convert Gray/RGB/CMYK input color spaces into RGB, CMYK, or DeviceN output components, clearing spot components when not explicitly set.
- Optional ICC profiles (`ProfileOut`, `ProfileRgb`, `ProfileCmyk`) are opened via Argyll-style ICC APIs and used for color conversion.
- `xcf_encode_color` / `xcf_decode_color` pack and unpack component values into `gx_color_index`.
- Params expose CRD defaults, separations, color profiles, process color model, and separation color names.
- `xcf_put_params` updates process model, separation list, component count, depth, and profile state.
- `xcf_get_color_comp_index` maps named process or separation components to component indices.
- XCF writer emits header, layer hierarchy, tile offsets, base image tile data, extra separation channels, fake reduced hierarchies, and channel metadata.

Notable implementation details:
- Tile size is fixed at 64x64.
- Base image data is stored as 3-byte RGB; extra separations are stored as separate channel planes.
- Extra channel bytes are inverted with `255 ^ value`, matching XCF channel semantics.
- `bpc_to_depth` rounds component packing to byte-compatible Ghostscript depths.
- Several `TO_DO_DEVICEN` comments indicate incomplete `SeparationOrder` behavior.

Filesystem relevance:
- Writes the final XCF stream through Ghostscript printer output `FILE *`. No filesystem internals.
