# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshtscr.c

Implements Type 1 screen halftone processing and screen enumeration.

Key functions:
- `gx_compute_cell_values`: derives halftone cell geometry, strip width/height, and shift values.
- `gs_setaccuratescreens`, `gs_currentaccuratescreens`: global AccurateScreens controls.
- `gs_setusewts`, `gs_currentusewts`: global WTS enable controls.
- `gs_setminscreenlevels`, `gs_currentminscreenlevels`: global minimum screen level controls.
- `gs_screen_order_init_memory`: computes cell size and allocates an order.
- `gs_screen_enum_init_memory`: prepares sampling transforms.
- `gs_screen_currentpoint`: returns next point for the spot function.
- `gs_screen_next`: records each sampled spot value.
- `gs_screen_install`: installs a completed sampled screen.

Cell selection:
- `pick_cell_size` maps requested frequency/angle through the device initial matrix, tries rounded integer cell vectors, evaluates frequency/angle error, enforces storage limits, and expands the repeat factor when needed.
- AccurateScreens continues searching beyond the first acceptable candidate.

Sampling behavior:
- Non-WTS screens sample a strip or full tile, then `gx_ht_construct_spot_order` finalizes the order.
- WTS screens delegate point and value enumeration to WTS routines.

Risks and quirks:
- AccurateScreens, WTS usage, and MinScreenLevels are global statics and explicitly noted as reentrancy problems.
- `FORCE_STRIP_HALFTONES` is a compile-time debug control.
