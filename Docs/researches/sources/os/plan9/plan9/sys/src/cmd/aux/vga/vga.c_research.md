# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vga.c

Generic VGA register access and base VGA controller implementation.

Key behavior:
- Provides safe wrappers for VGA port access:
  - `vgai`
  - `vgaxi`
  - `vgao`
  - `vgaxo`
- Handles attribute-controller read/write sequencing through `Status1`.
- `snarf()` reads generic VGA misc, feature, sequencer, CRTC, graphics, attribute, and optional palette state.
- `init()` computes baseline VGA register values from `Mode`:
  - misc sync polarity and fixed clock select,
  - sequencer state,
  - CRTC horizontal and vertical timing,
  - overflow bits,
  - interlace scaling,
  - display pitch from `virtx`,
  - graphics controller state,
  - attribute controller state,
  - optional palette.
- `load()` writes generic VGA registers and optional palette.
- `dump()` prints generic VGA state plus virtual size, panning, clock fields, memory aperture/base/size, and linear flag.

Integration:
- Exports `Ctlr generic` named `vga`.
- All SVGA controller files build on this state either directly or through `s3generic`.

Filesystem relevance:
- Indirect display utility code.
