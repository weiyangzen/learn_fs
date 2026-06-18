# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/rre.c

VNC server-side rectangle encoders for raw, RRE, CoRRE, and hextile.

Key responsibilities:
- Sends raw rectangles directly from the framebuffer.
- Encodes hextile updates by tiling into 16x16 blocks and choosing background, foreground, colored-subrect, or raw tile forms.
- Encodes RRE/CoRRE by splitting large rectangles and generating uniform-color subrectangles against a guessed background color.
- Falls back to raw encoding when compression would exceed raw size or allocation/classification fails.
- Counts expected rectangle splits for RRE/CoRRE/hextile.
- Implements pixel equality and pixel write helpers for 8-, 16-, and 32-bpp modes.

Important behavior:
- Background is estimated by sampling common colors.
- `encrre()` finds maximal same-color rectangles and marks covered pixels in a `done` array.
- CoRRE uses one-byte coordinates and smaller split dimensions.
- Hextile caches previous background/foreground colors but resets around raw/colorful cases for client compatibility.

Risks:
- Only 8/16/32 bpp are compressed; other depths fall back to raw.
- Compression is heuristic, not optimal.
