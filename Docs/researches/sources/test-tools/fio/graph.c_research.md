# sources/test-tools/fio/graph.c

## Purpose
Implements gfio's Cairo/GTK graph model and drawing routines. It supports bar graphs, line graphs, labels, colors, tick labels, unit-scaling callbacks, bounded history for live line graphs, and tooltip lookup for XY samples.

## Important APIs, Types, and Functions
Private state is held in `struct graph`, `struct graph_label`, `struct graph_value`, and `struct xyvalue`. Public functions from `graph.h` are implemented here: `graph_new`, `graph_set_size`, `graph_set_position`, `graph_set_font`, title setters, `graph_add_label`, `graph_add_data`, `graph_add_xy_data`, `graph_set_color`, `bar_graph_draw`, `line_graph_draw`, `graph_add_extra_space`, `line_graph_set_data_count_limit`, tooltip helpers, `graph_clear_values`, and `graph_free`. Important internal helpers include `graph_draw_common`, tick drawing, min/max scanners, `graph_label_add_value`, `graph_value_drop`, and priority-tree tooltip search.

## Control Flow
Callers create a graph, add labels, append values, optionally assign colors and axis callbacks, then draw into a Cairo context. Bar drawing computes one group per label and one bar per value. Line drawing scans all XY values for ranges, applies extra margins, records tick transforms, draws ticks and grid lines, then strokes each visible label's polyline. Tooltip insertion stores an X interval in a priority tree; lookup converts screen coordinates back into graph-space values using tick transform fields captured during the last draw and then chooses the closest Y match.

## State and Persistence Behavior
All state is in memory. Labels and values are heap-allocated and linked in fio `flist` lists. Tooltip-capable XY values are additionally indexed by `prio_tree_root`; duplicate X ranges become aliases on the existing priority-tree node. `per_label_limit` drops oldest samples when live graphs exceed the configured count. `graph_clear_values` drops values but retains labels, while `graph_free` frees titles and labels but does not free the `struct graph` object itself.

## Dependencies and Integration Points
Depends on Cairo, GTK, `tickmarks`, `cairo_text_helpers`, fio `flist`, and `lib/prio_tree`. It is used by gfio UI components to render bandwidth, latency, and other runtime charts.

## Risks
Several drawing paths divide by data ranges and assume non-empty labels or values; degenerate data is partly guarded with "No good data" fallbacks, but empty bar graphs can still produce unsafe label-width math. Tooltip correctness depends on a prior draw call to populate tick transform fields. `setstring()` assumes non-null strings. `graph_free()` omits `free(bg)`, so ownership expectations must stay clear. The code is not synchronized and is intended for UI-thread use.

## Test Signals
There are no direct unit tests in this subset. Useful coverage would render empty, single-valued, negative, all-zero, and bounded-history graphs; assert that tooltip lookup survives duplicate X ranges; run under ASan or Valgrind for add/drop/free cycles; and visually compare gfio charts.
