# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdps.c

This file implements Display PostScript view clipping support.

Functions:
- `gs_initviewclip` clears the active view clip path.
- `gs_viewclip` clips using winding-number rule.
- `gs_eoviewclip` clips using even-odd rule.
- `gs_viewclippath` replaces the current path with the current view clip path, or fabricates the default clip box if none is active.

`common_viewclip` is modeled after normal clipping code in `gspath.c`: it computes the current path bounding box, creates a rectangular clip path, clips it against the current path with the requested rule, assigns it to `pgs->view_clip`, and clears the current path.

Memory behavior is local and graphics-state owned. If allocation of the view clip path fails, it returns `gs_error_VMerror`.
