# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc.h

Shared private header for the Ghostscript Epson Stylus Color driver and its dithering modules.

Key contents:
- Defines `stc_pixel` as an unsigned integer type large enough for packed pixels.
- Defines `stc_t`, the auxiliary Stylus Color state block containing mode flags, bit depth, active dither algorithm, color-adjustment matrix, coding/transfer arrays, white patterns, algorithm names, ESC/P2 init/release strings, ESC/P2 geometry and resolution fields, print buffer state, and compression seed rows.
- Defines `stcolor_device`, combining Ghostscript common device/printer fields with `stc_t`.
- Defines flags for dither algorithm bits, CMYK10, unidirectional mode, hardware/software weave, compression mode, model variant, explicit ESC/P2 parameter fields, init/release override, and printed-data state.
- Defines the dither callback signature `stc_proc_dither`.
- Defines `stc_dither_t`, including algorithm name, callback, flags, required buffer expansion, and value range.
- Defines printer output bit masks for monochrome, RGB, and CMYK color bits.
- Defines `STC_TYPESWITCH` to dispatch byte/long/float algorithm value handling.
- Declares external dither routines: `stc_gsmono`, `stc_fs`, `stc_fscmyk`, `stc_gsrgb`, and `stc_fs2`.
- Defines the `STC_MODI` algorithm table extension entries for `gsmono`, `gsrgb`, `fsmono`, `fsrgb`, `fsx4`, `fscmyk`, and `fs2`.
- Defines default DPI and page margins for the Stylus Color driver.

Research notes:
- The header is deliberately shared by the core driver and separately compiled dithering routines.
- Adding a new dither algorithm requires declaration here, adding it to `STC_MODI`, and updating build dependencies.
- The model and color constants are local driver conventions, not Ghostscript-wide enums.
