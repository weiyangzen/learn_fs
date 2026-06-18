# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevphex.c

## Role

`gdevphex.c` is a Ghostscript ESC/P Raster printer driver for Epson Color Photo, Photo EX, and Photo 700 devices. It implements color mapping, microweave line scheduling, halftoning, raw device packing, RLE compression, and printer command emission.

## Device And Parameters

- Exposes `gs_photoex_device` named `photoex`.
- Supports `360x360`, `720x720`, and `1440x720` resolutions.
- Device parameters include `Depletion`, `Shingling`, `Render`, `Splash`, `Leakage`, `Binhibit`, and `DotSize`.
- Internal rendered color is CMYK; output device inks are six channels: black, cyan, magenta, yellow, light cyan, and light magenta.

## Color Mapping

- `photoex_map_rgb_color()` maps RGB to CMYK with black extraction, empirical transfer through `xtrans[]`, and hue-based compensation through `ctable[]`.
- `photoex_map_color_rgb()` maps packed CMYK back to RGB for Ghostscript queries, but intentionally is not the inverse transform.
- `Cmy2A()` computes a hue-angle-like value from CMY components for compensation interpolation.

## Page Pipeline

- `photoex_open()` sets margins based on physical printer width constraints, then calls `gdev_prn_open()`.
- `photoex_print_page()` validates resolution, clips printable width, allocates a large `RENDER` state, emits printer setup commands, chooses dot size, disables printer microweave, enables unidirectional mode, calls `RenderPage()`, ejects paper, resets, and frees buffers.
- `RenderPage()` repeatedly schedules head passes, ensures needed lines are halftoned, emits per-color band data, handles delayed vertical movement, horizontal offsets, and RLE output.

## Scheduling

- `SchedulerInit()`, `ScheduleLines()`, `ScheduleLeading()`, `ScheduleMiddle()`, `ScheduleTrailing()`, and `ScheduleBand()` implement line/nozzle assignment for 360, 720, and 1440 dpi.
- `start_720` and `start_1440` tables handle the leading edge of pages.
- The scheduler tracks which lines/phases have already printed with a modulo `MAX_MARK` mark array.

## Halftoning And Packing

- `HalftoneLine()` dispatches each CMYK channel through the selected halftoner, optionally letting black block color deposition, then packs output into raw six-ink bitplanes.
- `FloydSLine()` implements Floyd-Steinberg diffusion.
- `DitherLine()` implements 16x16 ordered dither using `dmatrix`.
- `BendorLine()` implements an experimental larger-kernel error diffusion with splash/leakage controls.
- `PackLine()` converts thresholded byte pixels into 1-bit raw lines and records active byte ranges.

## Printer Encoding

- `RleCompress()` and `RleFlush()` implement ESC/P Raster RLE packets.
- `SendReset()`, `SendMargin()`, `SendPaper()`, `SendGmode()`, `SendUnit()`, `SendUnidir()`, `SendMicro()`, `SendInk()`, `SendDown()`, `SendRight()`, `SendColour()`, and `SendData()` emit low-level ESC/P commands.

## Dependencies

Uses Ghostscript printer APIs, parameter APIs, `FILE` output, math helpers, direct raster access through `gdev_prn_get_bits()`, and static device-specific tables.

## Risks And Invariants

- The file itself notes several limitations: monochrome device incomplete, no TIFF compression, shingling/depletion unimplemented, hardcoded transfer/compensation, and experimental Bendor diffusion.
- Memory demand is high because `RENDER` contains large line caches and error buffers.
- Scheduling correctness depends on the constants for 32 nozzles and 8-line spacing.
- `RleCompress()` contains suspicious pointer/value handling in the repetitive sequence path, making this compression logic a risk area.
- `BendorLine()` assigns `leakage` from `dev->splash`, not `dev->leakage`, which appears inconsistent with the parameter documentation.
