# File Research: sources/os/plan9/9front/sys/src/cmd/proof/htroff.c

Troff device-independent output interpreter for the interactive `proof` previewer. It parses troff output, draws text and graphics into a Plan 9 window, manages pages/views/magnification, and supports navigation by buffering input offsets.

Key behavior:
- `readpage` interprets page, character, special character, numeric character, draw, font, size, motion, comment, and device-control commands.
- Draws lines, circles, ellipses, arcs, and splines with Plan 9 drawing primitives.
- `devcntrl` handles device name, resolution, and mounted fonts.
- `skipto` replays/skips input to reach requested pages while preserving font-loading side effects.
- `botpage` handles command strings for page navigation, magnification, view splitting, and offsets.

Integration points:
- Uses input buffering from `main.c`, UI commands from `screen.c`, and font drawing from `font.c`.
- Shares `offset`, `xyoffset`, `DIV`, `res`, `curfont`, `cursize`.

Risks:
- Page index cache fixed at 200 pages.
- Spline point array fixed at 300 points without explicit bounds guard.
- Parser exits on unknown input character, making preview brittle for unsupported troff extensions.
