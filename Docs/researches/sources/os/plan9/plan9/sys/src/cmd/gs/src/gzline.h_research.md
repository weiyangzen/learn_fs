# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzline.h

Small internal header for line parameters. It exposes the GC descriptor macro for `gx_line_params`, noting that the pattern pointer must only be followed when the pattern size is nonzero.

Exports:
- `private_st_line_params()`
- `st_line_params_num_ptrs`
- `gs_currentlineparams(const gs_imager_state *)`

This is graphics-state support for stroke parameters.
