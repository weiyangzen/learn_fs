# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevokii.c

Okidata IBM-compatible 9-pin dot-matrix printer driver.

- Defines `okiibm`, a 1-bit printer device with configurable compile-time defaults for X dpi 60/120/240 and Y dpi 72/144.
- Documents Okidata’s unusual 1/216-inch feed scaling to 1/144-inch physical movement and tracks this with `y_step`.
- `okiibm_print_page1` handles the main rendering loop: skips blank scan lines, emits vertical feed commands, copies 8 or 16 source lines, optionally shuffles high-resolution lines, transposes 8x8 blocks, trims trailing zero columns, and outputs graphics runs.
- Uses `gdev_prn_transpose_8x8` to convert row-major raster data into printer column format.
- `okiibm_output_run` emits ESC graphics commands and supports all columns, even columns, or odd columns for high horizontal resolution passes.
- `okiibm_print_page` builds init/end command strings and enables unidirectional printing for higher resolutions.
- Risk notes: vertical positioning depends on the printer starting in a power-on state; output assumes valid X dpi table indexing through `x_dpi / 60`.
