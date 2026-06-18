# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspcolor.c

Implements generic Pattern color-space support for Ghostscript.

Main behavior:
- Defines `gs_color_space_type_Pattern`.
- Initializes generic pattern templates with `gs_pattern_common_init`.
- Dispatches generic `gs_make_pattern` to PatternType-specific constructors.
- `gs_make_pattern_common` allocates a pattern instance, copies/saves graphics state, concatenates the pattern matrix, clears the path, assigns a pattern id, and stores the instance in the client color.
- Frees pattern instances with saved graphics states.
- `gs_setpattern` and `gs_setpatternspace` install pattern color state.
- `gs_pattern_reference` adjusts pattern instance reference counts.
- `gs_get_pattern` returns the template for PaintProc use.

Pattern color-space methods:
- Number of components is negative for Pattern spaces.
- Base color space may be embedded for uncolored patterns.
- Remapping delegates to PatternType-specific `remap_color`.
- Overprint is deferred for patterns and handled at set-device-color/set-color time.
- Serialization writes pattern-space type plus optional base color space.

Notable caveat: comment notes base-space setting in `gs_setpatternspace` is wrong, reflecting known design debt.
