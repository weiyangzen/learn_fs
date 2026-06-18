# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevepsn.c

## Role
`gdevepsn.c` implements monochrome Epson-compatible dot-matrix devices: `epson`, `eps9mid`, `eps9high`, and `ibmpro`.

## Device Definitions
- `gs_epson_device`: generic Epson 9/24-pin mode.
- `gs_eps9mid_device`: interleaved 9-pin mid-resolution mode.
- `gs_eps9high_device`: multi-pass interleaved 9-pin high-resolution mode.
- `gs_ibmpro_device`: IBM ProPrinter variant with different initialization and archaic behavior.

## Print Path
- Core logic is `eps_print_page`, parameterized by high/interleaved mode, initialization/end strings, archaic flag, and tab workaround flag.
- Valid graphics modes are selected from 9-pin and 24-pin mode tables based on X resolution.
- Reads bands from the Ghostscript printer buffer, skips vertical whitespace with `ESC J`, pads incomplete bands, and optionally shuffles/ORs scanlines for 9-pin interleaved modes.
- Transposes 8x8 blocks for printer column graphics, trims trailing blank output, and uses tab stops to compress horizontal whitespace when the printer supports them.
- `eps_output_run` emits Epson graphics commands, including double-density passes where only alternating columns are sent.
- Wrapper print functions supply initialization and ending sequences; `ibmpro_print_page` sends DC1 and line-spacing setup before rendering.

## Risks and Notes
- Returns `VMerror` on allocation failure.
- Compile-time `ARCHAIC` and `TAB_HICCUP` macros model old printer quirks.
- No filesystem behavior beyond streaming encoded raster output to `FILE *`.
