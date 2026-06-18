# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/graph.c

Renders server statistics graphs into `Memimage` objects for HTTP PNG output. It initializes memdraw resources, small font, solid-color fill images, and shared drawing lock state.

`statgraph()` bins stats through `binstats()`, derives graph dimensions and min/max bounds, draws axes and numeric labels, and renders each bin as a vertical high/low filled column. It supports caller-provided width, height, min/max, and fill palette selection.

The file is used by `httpd.c`'s `/graph` endpoint, which turns the returned `Memimage` into PNG.
