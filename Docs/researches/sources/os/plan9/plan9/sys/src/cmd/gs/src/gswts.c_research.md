# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gswts.c

Purpose: Generates Well Tempered Screening halftone cells and threshold arrays.

Key entry points:
- `wts_pick_cell_size()` chooses WTS cell parameters from a halftone screen and device matrix.
- `gs_wts_screen_enum_new()`, `gs_wts_screen_enum_currentpoint()`, and `gs_wts_screen_enum_next()` enumerate sample points and collect spot-function values.
- `wts_sort_cell()` sorts sampled thresholds uniformly.
- `wts_sort_blue()` applies BlueDot-style bump-based ordering.
- `wts_screen_from_enum()` converts an enum into runtime `wts_screen_t`.
- `gs_wts_free_enum()` and `gs_wts_free_screen()` free wrapper allocations.

Important internals:
- `gx_wts_cell_params_j_t` represents general-angle Screen J parameters, including jumps and probabilities.
- `gx_wts_cell_params_h_t` represents optimized Screen H parameters for zero/45-degree cases.
- Vector helpers (`wts_vec_*`) implement a lattice/GCD-like minimization used by Screen J cell selection.
- `wts_pick_cell_size_h()` uses simpler cell sizing optimized for near multiples of 45 degrees.
- `wts_pick_cell_size_j()` searches plausible cell widths/heights and jump vectors for general angles.
- `wts_blue_bump()` generates the bump map used by `wts_sort_blue()`.

Behavior:
- Converts halftone angle/frequency and CTM scaling into fast/slow UV vectors.
- Chooses Screen H when angle reduced modulo 45 degrees is nearly zero; otherwise Screen J.
- Stores sampled spot values as 32-bit thresholds, then rescales to `WTS_SORTED_MAX`.
- Includes `UNIT_TEST` code that can emit a PGM threshold image.

Dependencies:
- Uses `gxwts.h`, `gswts.h`, halftone state, math functions, `malloc/free/qsort`, and Ghostscript debug logging.

Notable risks:
- Uses raw `malloc/free`, not Ghostscript memory allocators.
- `gs_wts_free_enum()` frees only the enum struct, not the separately allocated `cell` buffer; similarly screen freeing only frees the top-level screen, not `samples`.
- `VERBOSE` is defined unconditionally, so debug-print code is compiled in.
