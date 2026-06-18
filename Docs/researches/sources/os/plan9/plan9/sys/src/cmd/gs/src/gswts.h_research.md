# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gswts.h

Purpose: Public/internal header for Well Tempered Screening generation.

Key definitions:
- Forward declares `gs_wts_screen_enum_t`.
- Defines `gx_wts_cell_params_t` with screen type, dimensions, and fast/slow UV vectors.

Declared API:
- `wts_pick_cell_size()`
- `gs_wts_screen_enum_new()`
- `gs_wts_screen_enum_currentpoint()`
- `gs_wts_screen_enum_next()`
- `wts_sort_blue()`
- `wts_sort_cell()`
- `wts_screen_from_enum()`
- `gs_wts_free_enum()`
- `gs_wts_free_screen()`

Dependencies:
- Relies on `wts_screen_type`, `wts_screen_t`, `gs_screen_halftone`, `gs_matrix`, `gs_point`, and `floatp` definitions from included users, especially `gxwts.h`/graphics headers.

Notable risks:
- Ownership rules are only implicit; callers must know allocations come from `malloc` in `gswts.c`.
