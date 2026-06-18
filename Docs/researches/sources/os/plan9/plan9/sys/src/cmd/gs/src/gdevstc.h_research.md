# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc.h

Purpose: Shared declarations and constants for the Epson Stylus Color driver family.

Key contents:
- Defines `stc_pixel`, `stc_t`, and `stcolor_device`.
- `stc_t` holds flags, bits/component, current dither algorithm, color adjustment matrix, coding/transfer arrays, computed lookup arrays, white-line patterns, exposed algorithm list, ESC/P2 strings/settings, print buffer sizes/state, buffered raster data, and delta-row seed buffers.
- Defines driver flags for algorithm selection bits, CMYK10, weave modes, compression modes, model variants, explicit ESC/P2 parameter overrides, and print state.
- Defines `stc_dither_t` and `stc_proc_dither`.
- Declares color constants for gray/RGB/CMYK output bytes.
- Provides `STC_TYPESWITCH` for byte/long/float algorithm buffer handling.
- Declares external dithering algorithms and assembles them into `STC_MODI`.
- Defines defaults for 360 dpi and paper margins.

Important dependencies:
- Included by the main driver and all Stylus dithering implementation files.

Notable risks / findings:
- Central coupling point: changes to flags, `STC_MODI`, or `stc_t` affect all Stylus driver files.
