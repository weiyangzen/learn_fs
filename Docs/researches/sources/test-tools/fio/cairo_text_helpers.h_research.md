# `sources/test-tools/fio/cairo_text_helpers.h`

Purpose: Declares Cairo text helper functions used by fio’s graphical frontend code.

Important APIs: Exposes `draw_centered_text()`, `draw_right_justified_text()`, `draw_left_justified_text()`, and `draw_vertical_centered_text()`, each taking a `cairo_t`, font name, x/y coordinates, font size, and text string.

Control flow and integration: Included by graph/printing UI modules that need aligned labels. The implementation is compiled into gfio-related objects when graphical support is enabled.

State and persistence: No state declared. Functions mutate the supplied Cairo context during drawing.

Dependencies: Includes `<cairo.h>` and therefore requires Cairo development headers in gfio builds.

Risks and test signals: Header is simple, but consumers must pass a valid Cairo context and non-null strings. Build tests should cover gfio enabled/disabled configurations; UI tests should check label placement.
