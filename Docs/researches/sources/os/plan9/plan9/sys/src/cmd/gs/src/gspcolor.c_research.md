# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspcolor.c

Implements generic Pattern color space support shared by PatternType 1 and 2.

Key functions and objects:
- GC descriptors for pattern templates/instances and Pattern color space.
- `gs_color_space_type_Pattern`: Pattern color space type vtable.
- `gs_pattern_common_init`: initializes pattern template common fields.
- `gs_make_pattern`: dispatches to pattern type’s `make_pattern`.
- `gs_make_pattern_common`: allocates pattern instance, copies graphics state, concatenates pattern matrix, clears path, assigns pattern ID.
- `rc_free_pattern_instance`: frees saved graphics state then instance.
- `gs_setpattern`, `gs_setpatternspace`.
- `gs_pattern_reference`, `gs_get_pattern`.
- Pattern color space procs: component count, base space, remap, init, restrict, install, overprint handling, refcount adjustment, serialization.

Integration:
- Includes color space, device color, path, image, stream, and state internals.
- Pattern color spaces may include a base paint color space for uncolored patterns.
- Pattern overprint setup is deferred to set-device-color for patterns.

Risk notes:
- Comment in `gs_setpatternspace` says base-space setting is wrong, indicating known design debt.
- `gx_adjust_color_Pattern` adjusts `pcc->pattern` without a null check in the visible code path.
- Pattern color spaces report negative component counts for backward compatibility, which downstream code must understand.
