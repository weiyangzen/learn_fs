# File Research: sources/os/plan9/9front/sys/src/cmd/grap/ticks.c

Tick and grid generation for `grap`. It stores explicit tick values/labels, selected sides, disabled sides, tick direction/length, and automatic tick settings. `ticks` updates automatic tick policy based on explicit tick statements.

Automatic ticks compute linear or logarithmic quantization for the default coordinate system. `iterator` expands explicit tick ranges. `print_ticks` formats labels, applies log side transforms, updates graph ranges, and emits per-side tick or grid pic lines through `maketick`. Grid descriptors reuse tick rendering with inside ticks and frame-spanning lengths.
