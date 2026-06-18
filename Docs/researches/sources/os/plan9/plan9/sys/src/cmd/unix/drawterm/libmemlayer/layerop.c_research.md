# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/layerop.c

Subdivides operations over visible and obscured layer regions.

Key functions:
- `_layerop`: recursively splits a screen rectangle around front layers; visible portions call the callback on the screen, obscured portions call it on save backing.
- `_memlayerop`: clips to layer screen rectangle and screen clip rectangle, then handles onscreen and offscreen pieces.

Important behavior:
- Assumes input rectangles were already clipped to logical layer bounds.
- If a layer is marked clear, operations go directly to the screen image.
- Offscreen portions are routed to save backing.
