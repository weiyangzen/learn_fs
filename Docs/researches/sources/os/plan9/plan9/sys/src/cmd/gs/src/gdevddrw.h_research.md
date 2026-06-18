# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevddrw.h

Declares shared default trapezoid-fill interfaces used by Ghostscript drawing code.

It defines `enum fill_trap_flags` with `ftf_peak0`, `ftf_peak1`, and `ftf_pseudo_rasterization`, then exposes `gx_fill_trapezoid_cf_fd` and `gx_fill_trapezoid_cf_nd`. These are the contiguous-fill, non-axis-swapped trapezoid implementations generated in `gdevddrw.c` through `gxdtfill.h`.

The header depends on surrounding Ghostscript types already visible to includers: `gx_device`, `gs_fixed_edge`, `fixed`, `gx_device_color`, and `gs_logical_operation_t`.

Risk is low; this is a narrow prototype header. Correctness depends on the generated implementations in `gdevddrw.c` matching the declared signatures.
