# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcldev.h

Internal command-list protocol and writer/reader support header. It defines bitmap compression modes, the command bytecode enum, command operand conventions, rectangle encodings, tile-depth encoding, bitmap padding policy, block-file entries, and per-band `gx_clist_state_s`.

The per-band state tracks current colors, saved device color, tile index/id/phase/colors, previous rectangle, logical operation, clipping, alpha-copy mode, known-state flags, command list, rendering cost, and colors used. The `known` flags integrate with path flags and include tile-parameter and begin-image knowledge. `cbuf_size` is fixed at 4096 and constrains bitmap/image command splitting.

The header declares clist driver procedures for rectangles, bitmap copy, masks/images, compositors, and band readback. It also exposes writer primitives for command allocation, command shortening, buffer flushing, variable-length integer encoding, color emission, tile colors/phase, logical operation, clipping, rectangle emission, bitmap emission, color maps, tile changes, halftone/color mapping, and band playback. The `FOR_RECTS`, `TRY_RECT`, and `HANDLE_RECT` macros encode per-band iteration plus two-stage VMerror recovery, making idempotent command emission a key invariant for callers.
