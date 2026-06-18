# `sources/test-tools/fio/cairo_text_helpers.c`

Purpose: Provides small Cairo text drawing helpers for gfio graph/printing UI code, handling horizontal and vertical text alignment around a point.

Important APIs and functions: Public functions are `draw_centered_text()`, `draw_right_justified_text()`, `draw_left_justified_text()`, and `draw_vertical_centered_text()`. Static `draw_aligned_text()` handles centered, left, and right horizontal alignment by measuring `cairo_text_extents_t` and adjusting the drawing origin.

Control flow: Each public horizontal helper delegates to `draw_aligned_text()` with an alignment constant. That helper selects a normal font face, sets font size, measures text, adjusts `x` and `y`, then calls `cairo_show_text()`. The vertical helper measures extents, adjusts coordinates, saves the Cairo state, translates to the pivot, rotates -90 degrees, translates back, draws text, and restores state.

State and persistence: Mutates the passed Cairo context’s font face, font size, current point, and temporarily its transformation matrix. `draw_vertical_centered_text()` restores transformations but not necessarily all text settings.

Dependencies and integration: Includes `cairo_text_helpers.h`, Cairo, GTK, and math for `M_PI`. Integrated into gfio/graphical output builds via the Makefile’s `GFIO_OBJS`.

Risks and test signals: Uses Cairo toy text API, so complex text shaping is not handled. Alignment depends on extents and may be font/backend-sensitive. Tests should render sample labels at each alignment and compare visually or by screenshot in gfio graph outputs.
