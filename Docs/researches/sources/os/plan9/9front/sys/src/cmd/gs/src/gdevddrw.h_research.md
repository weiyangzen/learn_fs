# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevddrw.h

Small Ghostscript header exposing selected polygon/trapezoid drawing declarations from `gdevddrw.c`.

Key contents:
- Defines `enum fill_trap_flags` with `ftf_peak0`, `ftf_peak1`, and `ftf_pseudo_rasterization`.
- Declares the contiguous-fill trapezoid entry points `gx_fill_trapezoid_cf_fd` and `gx_fill_trapezoid_cf_nd`.
- Uses Ghostscript geometry/color types supplied by surrounding headers: `gx_device`, `gs_fixed_edge`, `fixed`, `gx_device_color`, and `gs_logical_operation_t`.

Research notes:
- This is not a standalone public API header; it assumes inclusion in Ghostscript device/rendering compilation context.
- The two declared functions are generated in `gdevddrw.c` by including `gxdtfill.h` with `CONTIGUOUS_FILL` enabled.
