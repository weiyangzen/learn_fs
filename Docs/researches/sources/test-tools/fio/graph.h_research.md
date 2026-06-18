# sources/test-tools/fio/graph.h

## Purpose
Declares the public graphing API used by gfio to create, populate, draw, and query bar and line graphs.

## Important APIs, Types, and Functions
The header forward-declares `struct graph` and `struct graph_label`, exposes `graph_label_t`, defines `GRAPH_DEFAULT_FONT`, and declares lifecycle, sizing, position, title, label, data, color, axis callback, extra spacing, tooltip, base-offset, all-zero, and clear/free functions. `graph_axis_unit_change_callback` lets callers adjust axis titles when tick labels are scaled by powers of ten. `INVISIBLE_COLOR` marks a line as scale-affecting but not drawn.

## Control Flow
Typical use is `graph_new`, optional graph and title configuration, `graph_add_label`, repeated `graph_add_data` or `graph_add_xy_data`, drawing via `bar_graph_draw` or `line_graph_draw`, optional tooltip probing, and cleanup. Line graphs can also set a per-label data cap so append operations behave like a rolling window.

## State and Persistence Behavior
The API is purely in-memory and uses opaque structs to keep allocation and indexing details in `graph.c`. Callers retain label handles returned by `graph_add_label`, and those handles are invalid after label/free operations.

## Dependencies and Integration Points
The declarations reference `cairo_t` but do not include Cairo themselves in this file, so includers must have the relevant Cairo type visible. The API integrates with gfio UI code and fio's graph drawing support.

## Risks
Opaque pointer ownership is implicit: `graph_free()` frees internals but implementation does not free the graph object. `graph_set_font()` stores a pointer rather than duplicating it. Tooltip APIs depend on coordinates and tick state established by drawing.

## Test Signals
Compile-time coverage is the main signal. Runtime tests should exercise the API sequence from graph allocation through drawing and cleanup, plus rolling-window and tooltip functions.
