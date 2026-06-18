# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lalloc.c

Allocates a new layer image on a `Memscreen`.

Key function:
- `memlalloc`: creates a `Memimage` sharing the screen’s backing data, allocates `Memlayer`, optional save image, links it into the screen stack, moves it to front, and paints initial fill.

Important behavior:
- Layers with refresh functions do not allocate save backing.
- Starts new layers behind existing ones, then pulls them to the front to handle exposure correctly.
- Uses a static replicated `paint` image for fill color drawing.
