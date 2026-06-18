# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcsindex.c

Implements Indexed color space support.

`.setindexedspace` consumes a four-element color-space array and uses the current color space as the base space. It validates `hival`, rejects non-base-capable current spaces, and constructs a `gs_color_space_type_Indexed` color space.

Two lookup forms are supported:
- String lookup table: validates length, tolerates extra trailing bytes for compatibility, stores table pointer directly, and disables procedure lookup.
- Procedure lookup: validates executable procedure and calls `zcs_begin_map()` to allocate an indexed map and schedule cache population.

`indexed_map1()` is the continuation that repeatedly pushes the current index, runs the lookup procedure, collects returned component values, and writes them into `gs_indexed_map`.

The code uses `memmove()` for color-space parameter copying to avoid compiler aliasing issues noted in comments.

`zcs_begin_map()` is shared by indexed/tint map users. It allocates the map, initializes estack bookkeeping fields, and schedules the first continuation.

Main risk area: procedure-based maps are asynchronous and leave partially built data on the execution stack until all entries are sampled.
