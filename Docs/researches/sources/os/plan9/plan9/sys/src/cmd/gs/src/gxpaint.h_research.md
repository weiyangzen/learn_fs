# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpaint.h

`gxpaint.h` declares Ghostscript's internal fill/stroke interface. It forward-declares `gs_imager_state`, `gs_state`, `gx_device`, and `gx_device_color`, avoiding heavier includes.

The graphics-state-aware API consists of `gx_fill_path`, `gx_stroke_fill`, `gx_stroke_add`, and `gx_imager_stroke_add`. These are implemented in `gxpaint.c` and bridge high-level graphics state to lower-level device path operations.

The imager-level API includes `gx_adjust_if_empty` and `gx_stroke_path_expansion`, plus the compatibility macro `gx_stroke_expansion`. `gx_stroke_path_expansion` computes a conservative/exact fixed-point bbox expansion for stroke width, caps, and joins, returning errors when the expansion cannot fit.

The header defines `gx_fill_params` with rule, adjustment, flatness, and zero-width-fill behavior, plus `gx_fill_path_only` as a direct device-proc macro. It also defines `gx_stroke_params` and declares `gx_stroke_path_only`, which can either draw a stroke or construct a stroked outline path.

The file is purely contractual; implementation is split across `gxpaint.c`, `gxfill.c`, and `gxstroke.c`.
