# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzstate.h

Defines Ghostscript’s private `gs_state_s` graphics state. The imager state common prefix must be first, followed by saved-state linkage, CTM caches, paths, clipping paths, color state, font state, device state, transparency state, and client procs.

Important fields:
- `path`, `clip_path`, `clip_stack`, `view_clip`, and effective clip cache.
- `color_space`, `ccolor`, and `dev_color`.
- `font`, `root_font`, `char_tm`, cachedevice/charpath state.
- `device`, device filter stack, transparency group stack.
- `gs_state_do_ptrs` enumerates GC-managed pointers outside imager state and device.

This is a central object definition; correctness depends on GC enumeration order and the “imager state first” layout contract.
