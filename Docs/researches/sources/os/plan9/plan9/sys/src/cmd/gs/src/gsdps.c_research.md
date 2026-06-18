# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdps.c

## Role

`gsdps.c` implements Display PostScript view-clipping operations for Ghostscript.

## Main Functions

- `gs_initviewclip` clears the current view clip path if active.
- `gs_viewclip` applies winding-number view clipping.
- `gs_eoviewclip` applies even-odd view clipping.
- `gs_viewclippath` installs the current view clip path as the current path, or fabricates the default clip box if no view clip is active.

## Control Flow

`common_viewclip` mirrors ordinary clipping logic: allocate `pgs->view_clip` if missing, compute the current path bbox, create a temporary rectangular clip path, clip that against the current path under the selected rule, assign it to `view_clip`, and clear the current path.

## Dependencies

Uses path, clip-path, device, and graphics-state internals: `gspath.h`, `gzpath.h`, `gzcpath.h`, `gzstate.h`.

## Risks

The implementation comment says this is almost copied from `common_clip` and should ideally be merged. Divergence from normal clipping behavior is possible if one path evolves without the other.
