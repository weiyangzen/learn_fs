# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gshtscr.c

## Role

`gshtscr.c` implements Type 1 screen halftone sampling: choosing halftone cell geometry from requested frequency/angle and device matrix, allocating screen orders, enumerating sample points, accepting spot-function sample values, and installing completed screen orders.

This is graphics halftone infrastructure, not filesystem code.

## Main Interfaces

- Global controls: `gs_setaccuratescreens`, `gs_currentaccuratescreens`, `gs_setusewts`, `gs_currentusewts`, `gs_setminscreenlevels`, `gs_currentminscreenlevels`, `gs_gshtscr_init`.
- Cell/order setup: `gx_compute_cell_values`, `gs_screen_enum_alloc`, `gs_screen_init`, `gs_screen_init_memory`, `gs_screen_order_alloc`, `gs_screen_order_init_memory`, `gs_screen_enum_init_memory`.
- Enumeration/install: `gs_screen_currentpoint`, `gs_screen_next`, `gs_screen_install`.

## Core Behavior

- `pick_cell_size` searches integer cell vectors that approximate requested screen frequency/angle under device matrix scaling, tile-size limits, minimum level constraints, and accurate-screen preferences.
- `gx_compute_cell_values` derives super-cell dimensions, GCD values, and strip shifts from the selected cell parameters.
- `gs_screen_order_alloc` chooses either a full-tile allocation while sampling only a strip, or a strip-only allocation, based on cache memory limits.
- `gs_screen_currentpoint` maps device cell coordinates into spot-function coordinates, nudging sample positions to reduce equal spot values and handling WTS enumerators specially.
- `gs_screen_next` validates spot output in `[-1, 1]`, converts it to an internal sample value, records it in the order, and advances enumeration.

## Notable Risks

- `AccurateScreens`, `UseWTS`, and `MinScreenLevels` are file-static globals; comments explicitly state this harms reentrancy.
- The cell search is heuristic and can return `rangecheck` for small/degenerate frequencies or impossible tile constraints.
- `gs_screen_next` has a `long long` conversion and legacy commented alternative; behavior depends on the internal `ht_sample_t` range.
- WTS enumeration defers sorting until `gs_screen_currentpoint` returns completion.
