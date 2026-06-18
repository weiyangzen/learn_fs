# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzcpath.h

Defines internal clipping path structures. A `gx_clip_path` subclasses `gx_path`, adds a local/reference-counted rectangle list, fill rule, inner/outer bounds, path validity, high-level path list, and a change id.

Key types:
- `gx_clip_rect_list`: ref-counted rectangle list.
- `gx_cpath_path_list`: retained source paths for high-level devices.
- `gx_clip_path_s`: concrete clip path.
- `gs_cpath_enum_s`: iterator state for enumerating a clipping path as path or rectangles.

The file is tightly coupled to `gzpath.h` and Ghostscript GC descriptors.
