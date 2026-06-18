# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/print.c

This file finalizes generated graph output. `print` computes coordinate ranges, applies margins and log transforms, emits `xy_`, `x_`, and `y_` coordinate macros, emits frames/autoticks, and copies the temp file body to output.

`graph` flushes the previous graph, opens a new temp file, parses a graph name/position, and enforces capitalized graph names by warning. `setup` resets state at each `.G1` and injects initial definitions once.

`reset` preserves definitions and variables while clearing per-graph objects and visual state. `endstat` resets per-statement transient state such as label offsets, tick state, numeric list, and tick length.
