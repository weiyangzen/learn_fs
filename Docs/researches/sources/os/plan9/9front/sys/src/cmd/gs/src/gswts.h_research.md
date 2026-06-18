# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gswts.h

Declares the Well Tempered Screening public interface used by Ghostscript halftone code.

Key definitions:
- Opaque `gs_wts_screen_enum_t` and concrete `gx_wts_cell_params_t`.
- `gx_wts_cell_params_t` records screen type, cell width/height, and fast/slow UV basis increments.
- `wts_pick_cell_size` chooses screen cell parameters from halftone and device-matrix inputs.
- Screen-enumerator APIs expose the next spot-function point, accept a sampled value, sort the cell, convert to a `wts_screen_t`, and free enum/screen objects.

Dependencies:
- Expects `wts_screen_type`, `wts_screen_t`, `gs_screen_halftone`, `gs_matrix`, and `gs_point` to be available from including context and WTS/Ghostscript headers.
