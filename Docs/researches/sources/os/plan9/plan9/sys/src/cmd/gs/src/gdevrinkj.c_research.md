# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevrinkj.c

Purpose: Ghostscript printer device glue for the Rinkj inkjet pipeline, defaulting to a CMYK/DeviceN-style `rinkj` device at 720 dpi.

Key behavior:
- Defines `rinkj_device`, extending Ghostscript printer device state with color model, component names, separations, ICC output profile, setup file, and Rinkj setup state.
- Registers a mostly printer-forwarding device proc table, with custom params, color mapping, component lookup, color encode/decode, and `rinkj_print_page`.
- Supports `DeviceGray`, `DeviceRGB`, `DeviceCMYK`, and `DeviceN` color model selection via `ProcessColorModel`.
- Exposes and reads `ProfileOut`, `SetupFile`, `SeparationColorNames`, and separation-related params.
- Converts Ghostscript colorants to packed color indices and back, and provides mapping procs for RGB/CMYK/DeviceN workflows.
- Opens ICC profiles with the Argyll/ICC API and uses lookup objects for RGB/CMYK-to-CMYK conversion during output.
- Parses a Rinkj setup/config file, applying printer params and chained LUTs for planes named `KkCMcmY`.
- Builds an output chain `FILE -> RinkjByteStream -> Epson870 device -> screen/error-diffusion device`.
- During page output, pulls printer raster rows, splits planes, optionally applies ICC conversion with a 64K direct-mapped color cache, handles a 5th spot channel blend case, and writes split plane data.

Important dependencies:
- Ghostscript printer/device APIs: `gdevprn.h`, `gsparam.h`, color mapping structs, `gxdcconv.h`.
- ICC API: `icc.h`.
- Bundled Rinkj APIs: `rinkj-device`, `rinkj-byte-stream`, `rinkj-screen-eb`, `rinkj-epson870`.

Notable risks / findings:
- `rinkj_color_hash(color)` is called before `color` is assigned in the 3-plane and 5-plane ICC paths; this makes cache lookup undefined.
- `plane_data` allocates `n_planes_out` entries but frees only `n_planes_in`; RGB input with four output planes can leak.
- `gs_rinkj_device` initialization appears structurally suspicious: the initializer sequence after `bitspercomponent` does not visibly account for `n_planes_out`.
- LUT chain allocations are acknowledged as not freed.
